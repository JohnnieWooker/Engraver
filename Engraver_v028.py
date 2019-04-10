bl_info = {
    "name": "Engraver",
    "author":  "Lukasz Hoffmann <https://www.artstation.com/artist/lukaszhoffmann>",
    "version": (0, 28, 0),
    "blender": (2, 79, 0),
    "location": "",
    "description":"",
    "category": "Object"}

import bpy
from bpy.props import IntProperty, FloatProperty
import bmesh
import mathutils
from mathutils import Vector

depth=0.2
smooth=True
sharp=True
threshold=0.001
#interpolation='NEAREST_POLYNOR'
interpolation='POLYINTERP_NEAREST'

def similar(vector, vector1):
    issimilar=True
    if abs(vector[0]-vector1[0])>threshold:
        issimilar=False
    if abs(vector[1]-vector1[1])>threshold:
        issimilar=False
    if abs(vector[2]-vector1[2])>threshold:
        issimilar=False         
    return issimilar

def mirror(dupli,inversion_correction,apply_dt_mod,axis):
        selected = bpy.context.selected_objects
        for parent_o in selected:
            oldobname=parent_o.name   
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active=parent_o
            parent_o.select=True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            internal_selected = bpy.context.selected_objects 
            newobjects=[]
            oldobjects=[]               
            for o in internal_selected:
                oldobjects.append(o)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active=o      
                o.select = True
                if dupli:
                    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                if axis=='Y':
                    bpy.ops.transform.resize(value=(1, -1, 1), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='LINEAR', proportional_size=0.0630394)
                if axis=='X':
                    bpy.ops.transform.resize(value=(-1, 1, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='LINEAR', proportional_size=0.0630394)    
                if axis=='Z':
                    bpy.ops.transform.resize(value=(1, 1, -1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='LINEAR', proportional_size=0.0630394)
                    
                OBJ=bpy.context.scene.objects.active
                newobjects.append(OBJ)
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                OBJ_source=bpy.context.scene.objects.active                
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active=OBJ
                OBJ.select = True
                if inversion_correction:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.reveal()
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.flip_normals()
                    #bpy.ops.mesh.normals_make_consistent(inside=bpy.context.scene.inversion_correction_inside)
                    bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                modifier=OBJ.modifiers.new(name='CUSTOM_DT_MIRROR',type='DATA_TRANSFER')
                modifier.object=OBJ_source
                modifier.use_loop_data=True
                modifier.data_types_loops={'CUSTOM_NORMAL'}
                if apply_dt_mod:           
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    bpy.data.objects.remove(OBJ_source, True)
            bpy.ops.object.select_all(action='DESELECT')
            try:
                bpy.context.scene.objects.active=oldobjects[0]
            except:
                print("Object is empty")  
            for o in oldobjects:
                o.select=True
                print(o.name)
            bpy.context.scene.objects.active.name=oldobname                    
            bpy.ops.object.join()        
            bpy.ops.object.select_all(action='DESELECT')
            try:
                bpy.context.scene.objects.active=newobjects[0]
            except:
                print("Object is empty")  
            for o in newobjects:
                o.select=True
                print(o.name)                
            bpy.ops.object.join()    
        return {'FINISHED'}   

def fillvect(OBJvect):
    bpy.ops.object.select_all(action='DESELECT')
    OBJvect.select=True
    bpy.context.scene.objects.active=OBJvect
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type="VERT") 
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
 
def sameside(p1,p2,a,b):
    t1=b-a
    t2=p1-a
    cp1=(b-a).cross(p1-a)
    cp2=(b-a).cross(p2-a)
    if cp1.dot(cp2)>=0:
        return True
    else:
        return False

def pitvolume(p,a,b,c):
    isontr=False
    if pit(mathutils.Vector((p[0],p[1],0)),mathutils.Vector((a[0],a[1],0)),mathutils.Vector((b[0],b[1],0)),mathutils.Vector((c[0],c[1],0))):
        if pit(mathutils.Vector((p[0],0,p[2])),mathutils.Vector((a[0],0,a[2])),mathutils.Vector((b[0],0,b[2])),mathutils.Vector((c[0],0,c[2]))):
            if pit(mathutils.Vector((0,p[1],p[2])),mathutils.Vector((0,a[1],a[2])),mathutils.Vector((0,b[1],b[2])),mathutils.Vector((0,c[1],c[2]))):
                isontr=True
    return isontr        
def pit(p,a,b,c):
    if sameside(p,a,b,c) and sameside(p,b,a,c) and sameside(p,c,a,b):
        return True
    else:
        return False    

def makecage(OBJ,thick):
    bpy.ops.object.select_all(action='DESELECT')
    OBJ.select=True
    bpy.context.scene.objects.active=OBJ
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)    
    OBJcage= OBJ.copy()
    OBJcage.data = OBJ.data.copy() 
    bpy.context.scene.objects.link(OBJcage)
    #inflating cage mesh
    mod_solid = OBJcage.modifiers.new("SOLIDIFY", 'SOLIDIFY')
    mod_solid.thickness=thick    
    mod_solid.offset=0
    mod_displace=OBJcage.modifiers.new("DISPLACE", 'DISPLACE') 
    mod_displace.mid_level=1-thick/2    
    bpy.ops.object.select_all(action='DESELECT')
    OBJcage.select=True
    bpy.context.scene.objects.active=OBJcage
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    mod_displace.strength=0.2   
    bpy.ops.object.modifier_apply(modifier=mod_solid.name)
    bpy.ops.object.modifier_apply(modifier=mod_displace.name)   
    OBJcage.hide=True
    bpy.ops.object.select_all(action='DESELECT')
    return OBJcage

def is_inside(point,ob):
    axes = [ mathutils.Vector((1,0,0)) ]
    outside = False
    for axis in axes:
        mat = ob.matrix_world
        mat.invert()
        #mat = mathutils.Matrix(ob.matrix_world).invert()
        orig = mat*point
        mat.invert()
        count = 0
        while True:
            hit,location,normal,index = ob.ray_cast(orig,orig+axis*10000.0)
            if index == -1: break
            count += 1
            orig = location + axis*0.00001
        if count%2 == 0:
            outside = True
            break
    return not outside

def vertsinside(OBJsurf,OBJcage):
    verts=[]
    bm = bmesh.new()
    bm.from_mesh(OBJsurf.data)
    mat = OBJsurf.matrix_world
    verts_to_rem=[]
    verts_to_rem_id=[]
    for v in bm.verts:
        if (is_inside(v.co*mat,OBJcage)):
            verts_to_rem.append(v)
            verts_to_rem_id.append(v.index)
            for l in v.link_edges:
                for i in l.verts:
                    verts.append(i.co*mat)
                    for il in i.link_edges:
                        for ii in il.verts:
                            verts.append(ii.co*mat)
    return verts, verts_to_rem, verts_to_rem_id   

def smartbool(operation):
    if len(bpy.context.selected_objects)==2 and bpy.context.active_object.mode=='OBJECT':
        OBJdest=bpy.context.scene.objects.active
        OBJactor=bpy.context.selected_objects[0]
        if OBJdest==OBJactor:
            OBJactor=bpy.context.selected_objects[1]    
        
        #create destination duplicate normal source            
        OBJdest_source=OBJdest.copy()
        OBJdest_source.data = OBJdest.data.copy()
        bpy.context.scene.objects.link(OBJdest_source)
        OBJdest_source.hide=True
        
         #create actor duplicate normal source            
        OBJactor_source=OBJactor.copy()
        OBJactor_source.data = OBJactor.data.copy()
        bpy.context.scene.objects.link(OBJactor_source)        
        OBJactor_source.hide=True
        
        #select all in destination
        OBJdest.select=True   
        bpy.context.scene.objects.active=OBJdest
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')        
        bpy.ops.object.mode_set(mode='OBJECT')
        #deselect all in actor
        OBJactor.select=True   
        bpy.context.scene.objects.active=OBJactor
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #create boolean modifier
        mod_boolean = OBJdest.modifiers.new("SMART_BOOLEAN", 'BOOLEAN')
        mod_boolean.operation=operation
        mod_boolean.object=OBJactor        
        
        #invert actor if boolean operation is difference
        if operation=='DIFFERENCE':
            bpy.ops.object.select_all(action='DESELECT')
            OBJactor_source.hide=False
            OBJactor_source.select=True   
            bpy.context.scene.objects.active=OBJactor_source         
            mirror(False,False,True,'X')            
            bpy.ops.transform.resize(value=(-1, 1, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='LINEAR', proportional_size=0.0630394)    
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)            
            OBJactor_source.hide=True
            OBJdest_source.hide=True
        #collapse mod
        bpy.ops.object.select_all(action='DESELECT')
        OBJdest.select=True   
        bpy.context.scene.objects.active=OBJdest
        bpy.ops.object.modifier_apply(modifier=mod_boolean.name)        
        matrix_dest_source=OBJdest_source.matrix_world.to_translation()
        matrix_actor_source=OBJactor_source.matrix_world.to_translation()
        mats=bpy.context.active_object.matrix_world
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE") 
        dest_verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
        dest_verts_co=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
        if sharp:
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.mesh.select_mode(type="VERT") 
            for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                if i.co in dest_verts_co:
                    i.select=True
            bpy.ops.mesh.select_linked(delimit={'SHARP'})
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.join()
            mats=bpy.context.active_object.matrix_world
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type="VERT")             
            mats=bpy.context.active_object.matrix_world
            actor_verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
            actor_verts_co = [mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]    
            bpy.ops.mesh.hide(unselected=False)
            
            for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                for j in actor_verts_co: 
                    if similar(mats*i.co,j):
                        i.select=True
            bpy.ops.mesh.select_linked(delimit={'SHARP'})
            dest_verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
            dest_verts_co=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
            bpy.ops.mesh.reveal()
        
        if not sharp:    
            bpy.ops.mesh.select_all(action='INVERT')
            actor_verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
            actor_verts_co = [mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
        
        #removing redundant vertex group
        vg_old = OBJdest.vertex_groups.get('Normal_Transfer_Dest')
        if vg_old is not None:
            OBJdest.vertex_groups.remove(vg_old)
        vg_old = OBJdest.vertex_groups.get('Normal_Transfer_Actor')
        if vg_old is not None:
            OBJdest.vertex_groups.remove(vg_old)                
            
        #adding selected to vgs
        vg_dest = bpy.context.active_object.vertex_groups.new(name="Normal_Transfer_Dest")
        bpy.ops.object.mode_set(mode='OBJECT') 
        vg_dest.add(dest_verts, 1.0, 'ADD')   
        vg_actor = bpy.context.active_object.vertex_groups.new(name="Normal_Transfer_Actor")
        vg_actor.add(actor_verts, 1.0, 'ADD') 
        
        #clearing redundant poly inside actor source mesh
        bpy.ops.object.select_all(action='DESELECT')
        OBJactor_source.hide=False
        OBJactor_source.select=True   
        bpy.context.scene.objects.active=OBJactor_source
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        mats=bpy.context.active_object.matrix_world
        bm=bmesh.from_edit_mesh(bpy.context.active_object.data).verts   
        
        for i in bm:
            print(mats*i.co)
        print('sec')    
        for i in actor_verts_co:
            print(i)  
        
        for i in bm:
            count=0
            index=0            
            for j in actor_verts_co:
                if  similar(mats*i.co,j):                    
                    count=count+1 
                if count==1:
                    i.select=True
                if count==2:                  
                    i.select=False    
            if count==1:
                break     
        #return{'FINISHED'}    
        bpy.ops.mesh.select_linked(delimit={'SHARP'})    
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT') 
        OBJactor_source.hide=True
        
                
        #clearing redundant poly inside destination source mesh
        bpy.ops.object.select_all(action='DESELECT')
        OBJdest_source.hide=False
        OBJdest_source.select=True   
        bpy.context.scene.objects.active=OBJdest_source
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        mats=bpy.context.active_object.matrix_world
        bm=bmesh.from_edit_mesh(bpy.context.active_object.data).verts  
        """
        for i in bm:
            print(mats*i.co)
        print("sec")    
        for i in dest_verts_co:
            print(i) 
        """           
        for i in bm:
            count=0
            index=0
            for j in dest_verts_co:
                if  similar(mats*i.co,j):                    
                    count=count+1 
                if count==1:
                    i.select=True
                if count==2:                  
                    i.select=False    
            if count==1:
                break     
        bpy.ops.mesh.select_linked(delimit={'SHARP'})         
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT') 
        OBJdest_source.hide=True
        
        #sharpen intersection
        bpy.ops.object.select_all(action='DESELECT')
        OBJdest.select=True   
        bpy.context.scene.objects.active=OBJdest
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type="EDGE") 
        #passing normals from actor
        bpy.ops.object.mode_set(mode='OBJECT')
        mod_DataTransfer_actor = bpy.context.active_object.modifiers.new("DATATRANSFER", 'DATA_TRANSFER')
        mod_DataTransfer_actor.object=OBJactor_source
        mod_DataTransfer_actor.use_loop_data=True        
        mod_DataTransfer_actor.data_types_loops={'CUSTOM_NORMAL'} 
        mod_DataTransfer_actor.loop_mapping = interpolation
        mod_DataTransfer_actor.vertex_group = vg_actor.name      
        if smooth:          
            bpy.context.active_object.data.use_auto_smooth = 1
            bpy.context.active_object.data.auto_smooth_angle=180 
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_DataTransfer_actor.name)
        OBJactor_source.hide=False
        bpy.data.objects.remove(OBJactor_source, True)
        
        #passing normals from destination
        mod_DataTransfer_actor = bpy.context.active_object.modifiers.new("DATATRANSFER", 'DATA_TRANSFER')
        mod_DataTransfer_actor.object=OBJdest_source
        mod_DataTransfer_actor.use_loop_data=True
        mod_DataTransfer_actor.data_types_loops={'CUSTOM_NORMAL'} 
        mod_DataTransfer_actor.loop_mapping = interpolation
        mod_DataTransfer_actor.vertex_group = vg_dest.name
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_DataTransfer_actor.name)
        OBJdest_source.hide=False
        bpy.data.objects.remove(OBJdest_source, True)
        
    return{'FINISHED'}

class jwbooldiff(bpy.types.Operator):
    bl_idname="jw.booldiff"
    bl_label="Difference"
    def execute(self,context):
        smartbool("DIFFERENCE")
        return{'FINISHED'}
    
class jwboolunion(bpy.types.Operator):
    bl_idname="jw.boolunion"
    bl_label="Union"
    def execute(self,context):
        smartbool("UNION")
        return{'FINISHED'} 
    
class jwboolintersect(bpy.types.Operator):
    bl_idname="jw.intersect"
    bl_label="Intersect"
    def execute(self,context):
        smartbool("INTERSECT")
        return{'FINISHED'} 
    
class jwmirrorx(bpy.types.Operator):
    bl_idname="jw.mirrorx"
    bl_label="X"
    def execute(self,context):
        mirror(False,True,True,'X')
        return{'FINISHED'}  
    
class jwmirrory(bpy.types.Operator):
    bl_idname="jw.mirrory"
    bl_label="Y"
    def execute(self,context):
        mirror(False,True,True,'Y')
        return{'FINISHED'}  
    
class jwmirrorz(bpy.types.Operator):
    bl_idname="jw.mirrorz"
    bl_label="Z"
    def execute(self,context):
        mirror(False,True,True,'Z')
        return{'FINISHED'}                  
    
class jwbooleans(bpy.types.Menu):
    bl_idname="jw.booleans"
    bl_label="Booleans"
    def draw(self, context):        
        layout = self.layout
        layout.label("Booleans")
        layout.operator(jwbooldiff.bl_idname)
        layout.operator(jwboolunion.bl_idname)
        layout.operator(jwboolintersect.bl_idname)
        
class jwmirrors(bpy.types.Menu):
    bl_idname="jw.mirrors"
    bl_label="Mirror"
    def draw(self, context):        
        layout = self.layout
        layout.label("Mirror")
        layout.operator(jwmirrorx.bl_idname)    
        layout.operator(jwmirrory.bl_idname)    
        layout.operator(jwmirrorz.bl_idname)
        
class jwsettings(bpy.types.Menu):
    bl_idname="jw.settings"
    bl_label="Settings"
    def draw(self, context):        
        layout = self.layout
        layout.label("Settings")  
        layout.prop(context.scene, "depth_prop")         

def separate(self,OBJvect):
    bpy.ops.object.select_all(action='DESELECT')
    OBJvect.select=True  
    bpy.context.scene.objects.active=OBJvect
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()    
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    return(bpy.context.selected_objects)    

def addalltovg(OBJsurf):    
    all_verts=[]
    bpy.ops.object.select_all(action='DESELECT')
    OBJsurf.select=True  
    bpy.context.scene.objects.active=OBJsurf
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    vg_old = OBJsurf.vertex_groups.get('All_Old')
    if vg_old is not None:
        OBJsurf.vertex_groups.remove(vg_old)
    all_verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]      
    vg = bpy.context.active_object.vertex_groups.new(name="All_Old")
    bpy.ops.object.mode_set(mode='OBJECT') 
    vg.add(all_verts, 1.0, 'ADD')        
    return vg

class jwinsertoperator(bpy.types.Operator):
    bl_idname="jw.insert"
    bl_label="Engrave"
    def modal(self,context,event):
        return{'FINISHED'}
    def invoke(self,context,event):
        if len(bpy.context.selected_objects)==2 and bpy.context.active_object.mode=='OBJECT':    
            #bpy.ops.object.transform_apply(location=True, rotation=True, scale=False) 
            OBJsurf=bpy.context.scene.objects.active
            OBJvect=bpy.context.selected_objects[0]
            if OBJsurf==OBJvect:
                OBJvect=bpy.context.selected_objects[1]
            #separate decal
            decals=separate(self,OBJvect)
            
            for OBJvect in decals:

                self.OB_NAME=OBJvect.name
                self.OBJsurf_NAME=OBJsurf.name
                self.OBJvect_NAME=OBJvect.name     
                #create duplicate normal source            
                OBJsource=OBJsurf.copy()
                OBJsource.data = OBJsurf.data.copy()
                bpy.context.scene.objects.link(OBJsource)
                self.OBJsource_NAME=OBJsource.name
                OBJsource.hide=True            
                bpy.ops.object.select_all(action='DESELECT')
                OBJvect.select=True   
                bpy.context.scene.objects.active=OBJvect
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type="VERT") 
                bpy.ops.mesh.select_non_manifold()
                vmat=OBJvect.matrix_world
                self.manifold_vect = [vmat*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select] 
                bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                bpy.ops.mesh.fill()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')
                OBJvect.select=False
                OBJcagetemp=bpy.context.selected_objects[0]
                thick=(((OBJsurf.dimensions[0]+OBJvect.dimensions[0])/2+(OBJsurf.dimensions[1]+OBJvect.dimensions[1])/2+(OBJsurf.dimensions[2]+OBJvect.dimensions[2])/2)/3)/10            
                OBJcage=makecage(OBJcagetemp,thick) 
                bpy.data.objects.remove(OBJcagetemp, True) 
                self.OBJcage_NAME=OBJcage.name
                self.sens_multi=((OBJcage.dimensions[0]+OBJcage.dimensions[1]+OBJcage.dimensions[2])/3)*10
                                
                #adding all vertices to vg for further detection of new ones
                vg=addalltovg(OBJsurf)
                
                #deselect surface verts for  sake of proper detection of verts created by boolean operation                
                bpy.ops.object.select_all(action='DESELECT')
                OBJsurf.select=True  
                bpy.context.scene.objects.active=OBJsurf
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                vlen_old=len(bmesh.from_edit_mesh(bpy.context.active_object.data).verts)
                bpy.ops.object.mode_set(mode='OBJECT')   
                             
                #boolean operation
                bool_mod = OBJsurf.modifiers.new("BOOLEAN", 'BOOLEAN')
                bool_mod.object=OBJcage
                bool_mod.operation = 'DIFFERENCE'  
                bool_mod.double_threshold=0           
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bool_mod.name)                
                 
                #remove redundant geometry 
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete(type='FACE') 
            
                #selecting border vertices
                mats=bpy.context.active_object.matrix_world
                OBJsurf.vertex_groups.active_index=vg.index
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.select_all(action='INVERT')
                self.manifold_surf=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]                
                    
                #expanding selection to linked and ading verts to group        
                bpy.ops.mesh.select_linked(delimit={'SHARP'})
                bpy.ops.mesh.select_less()
                self.normal_surf=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
                bpy.ops.mesh.select_all(action='DESELECT')   
                
                #reselecting border vertices
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                    if mats*i.co in self.manifold_surf:
                        i.select=True 
                        
                #clearing cage mesh
                bpy.data.objects.remove(OBJcage, True)     
                #cleared cage mesh
                                         
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                    
                #adding internal surface verts to vg
                bpy.context.scene.objects.active=OBJvect
                OBJvect.select=True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_non_manifold()
                
                #revealing and merging meshes
                bpy.ops.object.mode_set(mode='OBJECT')
                OBJ_source=bpy.data.objects[self.OBJsource_NAME]
                bpy.ops.object.select_all(action='DESELECT') 
                OBJvect.select=True
                OBJsurf.select=True
                bpy.context.scene.objects.active=OBJsurf
                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode='EDIT')   
                
                #removing redundant vertex group
                vg_old = OBJsurf.vertex_groups.get('Normal_Transfer')
                if vg_old is not None:
                    OBJsurf.vertex_groups.remove(vg_old)
                
                #adding selected to vg and filling gap 
                verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select or mats*i.co in self.normal_surf]      
                vg = bpy.context.active_object.vertex_groups.new(name="Normal_Transfer")
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.fill()
                
                bpy.ops.object.mode_set(mode='OBJECT') 
                vg.add(verts, 1.0, 'ADD')        
                
                bpy.ops.object.mode_set(mode='OBJECT')
                mod_DataTransfer = bpy.context.active_object.modifiers.new("DATATRANSFER", 'DATA_TRANSFER')
                mod_DataTransfer.object=OBJ_source
                mod_DataTransfer.use_loop_data=True
                mod_DataTransfer.data_types_loops={'CUSTOM_NORMAL'} 
                mod_DataTransfer.loop_mapping = 'POLYINTERP_NEAREST'
                mod_DataTransfer.vertex_group = vg.name   
                if smooth:             
                    bpy.ops.object.shade_smooth()
                    bpy.context.active_object.data.use_auto_smooth = 1
                    bpy.context.active_object.data.auto_smooth_angle=180 
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_DataTransfer.name)
                OBJ_source.hide=False
                bpy.data.objects.remove(OBJ_source, True)
            return{'FINISHED'}
    
class jwcutoperator(bpy.types.Operator):
    bl_idname="jw.cut"
    bl_label="Cut"  
    def invoke(self,context,event):
        if len(bpy.context.selected_objects)==2 and bpy.context.active_object.mode=='OBJECT':
            OBJsurf=bpy.context.scene.objects.active
            OBJvect=bpy.context.selected_objects[0]
            if OBJsurf==OBJvect:
                OBJvect=bpy.context.selected_objects[1] 
            decals=separate(self,OBJvect) 
            for OBJvect in decals:
                bpy.ops.object.select_all(action='DESELECT')
                OBJvect.select=True   
                bpy.context.scene.objects.active=OBJvect
                bpy.ops.object.mode_set(mode='EDIT')   
                bpy.ops.mesh.select_mode(type="VERT") 
                bpy.ops.mesh.select_all(action='SELECT')
                thick=(OBJvect.dimensions[0]+OBJvect.dimensions[1]+OBJvect.dimensions[1]+OBJvect.dimensions[2])/3*context.scene.depth_prop/10
                bpy.ops.mesh.inset(thickness=thick)
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.transform.edge_slide(use_clamp=False, value=-1, mirror=False, correct_uv=True, single_side=True, release_confirm=True) 
                bpy.ops.mesh.select_mode(type="EDGE") 
                #finding selected verts for further deselect
                edges_sel=[i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).edges if i.select]    
                old_vert_count=len(bmesh.from_edit_mesh(bpy.context.active_object.data).verts)                            
                
                bpy.ops.mesh.select_more(use_face_step=False)
                
                #deselecting old edges
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).edges:
                    if i.index in edges_sel:
                        i.select=False
                        
                #subdividing        
                bpy.ops.mesh.select_mode(type="EDGE") 
                bpy.ops.mesh.subdivide(smoothness=0)
                
                #selecting internal loop
                bpy.ops.mesh.select_mode(type="VERT") 
                print(old_vert_count)
                bpy.ops.mesh.select_all(action='DESELECT')
                insens_verts=[]
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                    if i.index >= old_vert_count:
                        i.select=True    
                        insens_verts.append(i.index)
                #adding to vg
                vg_old = OBJvect.vertex_groups.get('normal_insesitive')
                if vg_old is not None:
                    OBJvect.vertex_groups.remove(vg_old)
                vg_vect_insens = bpy.context.active_object.vertex_groups.new(name="normal_insesitive")
                bpy.ops.object.mode_set(mode='OBJECT')   
                vg_vect_insens.add(insens_verts, 1.0, 'ADD')  
                bpy.ops.object.mode_set(mode='EDIT')   
                #adding volume
                bpy.ops.transform.shrink_fatten(value=thick, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
                
                #adding neighbour edges and verts to selection
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).edges:
                    if i.verts[0].select and i.verts[1].select:
                        i.select=True
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).edges:
                    if i.index in edges_sel:
                        i.verts[0].select=True        
                        i.verts[1].select=True        
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).faces:  
                    if i.verts[0].select and i.verts[1].select and i.verts[2].select and i.verts[3].select:
                        i.select=True    
                            
                        
                #ripping apart
                bpy.ops.mesh.separate(type='SELECTED')
                
                #Transfering normals
                bpy.ops.object.mode_set(mode='OBJECT')
                mod_DataTransfer = bpy.context.active_object.modifiers.new("DATATRANSFER", 'DATA_TRANSFER')
                mod_DataTransfer.object=OBJsurf
                mod_DataTransfer.use_loop_data=True
                mod_DataTransfer.data_types_loops={'CUSTOM_NORMAL'} 
                mod_DataTransfer.loop_mapping = 'POLYINTERP_NEAREST'
                mod_DataTransfer.vertex_group = vg_vect_insens.name   
                mod_DataTransfer.invert_vertex_group = True
                if smooth:             
                    bpy.ops.object.shade_smooth()
                    bpy.context.active_object.data.use_auto_smooth = 1
                    bpy.context.active_object.data.auto_smooth_angle=180 
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_DataTransfer.name)    
                
                OBJvect.select=False
                
                #working on outer geometry
                
                #filling gap in outer ring
                OBJvect=bpy.context.selected_objects[0]
                bpy.context.scene.objects.active=OBJvect
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.vertex_group_set_active(group='normal_insesitive')
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.edge_face_add()                        
                
                #invoking engrave class
                
                bpy.ops.object.mode_set(mode='OBJECT')
                OBJsurf.select=True
                bpy.context.scene.objects.active=OBJsurf                
                bpy.ops.jw.insert('INVOKE_DEFAULT')
                
        return{'FINISHED'}        

    
class jwcarveoperator(bpy.types.Operator):    
    bl_idname="jw.carve"
    bl_label="Engrave flat"
    first_mouse_x = IntProperty()
    phase=IntProperty()
    phase=1
    OBJsurf_NAME=""
    OBJvect_NAME=""
    OBJsource_NAME=""
    OBJcage_NAME=""
    sensitivity=1000
    sens_multi=1
    selected=[]
    face_selected=[]
    face_selected_indices=[]
    avg_normal=[]
    manifold_vect=[]
    manifold_surf=[]
    normal_surf=[]
    masked=[]
    def modal(self, context, event):    

        if event.type == 'MOUSEMOVE':        
            if event.shift:
                self.sensitivity=10000/self.sens_multi*5
            if self.phase==1:
                delta = self.first_mouse_x - event.mouse_x
                #print(delta)
                bpy.ops.mesh.dissolve_verts()
                bpy.ops.mesh.select_all(action='SELECT')            
                bpy.ops.mesh.inset(thickness=abs(delta)/self.sensitivity)
                bpy.ops.transform.shrink_fatten(value=delta/self.sensitivity, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            if self.phase==2 or self.phase==3:                              
                delta = self.first_mouse_x - event.mouse_x                
                bpy.ops.mesh.dissolve_verts()
                bpy.ops.mesh.select_all(action='DESELECT') 
                for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                    if v.co in self.face_selected_indices:
                        v.select=True       
                for v in bmesh.from_edit_mesh(bpy.context.active_object.data).faces:
                    sel=True                    
                    for f in v.verts:                        
                        if not f.select:
                            sel=False
                    if sel:
                        v.select=True                    
                bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, delta/self.sensitivity*(-1)), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})        
                self.phase=3
            self.sensitivity=1000/self.sens_multi*5

        if event.type in {'LEFTMOUSE'} and event.value in {'RELEASE'}:
            if self.phase==4:
                return{'CANCELLED'}
                self.phase=1
            if self.phase==3:    
                OBJvect = bpy.data.objects[self.OBJvect_NAME]
                OBJsurf = bpy.data.objects[self.OBJsurf_NAME]
                OBJcage = bpy.data.objects[self.OBJcage_NAME]
                OBJsurf.hide=False
                                
                #adding all vertices to vg for further detection of new ones
                bpy.ops.object.mode_set(mode='OBJECT')
                vg=addalltovg(OBJsurf)
                
                #deselect surface verts for  sake of proper detection of verts created by boolean operation
                bpy.ops.object.select_all(action='DESELECT')
                OBJsurf.select=True  
                bpy.context.scene.objects.active=OBJsurf
                bpy.ops.object.mode_set(mode='EDIT')
                vlen_old=len(bmesh.from_edit_mesh(bpy.context.active_object.data).verts)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                
                #boolean operation
                bool_mod = OBJsurf.modifiers.new("BOOLEAN", 'BOOLEAN')
                bool_mod.object=OBJcage
                bool_mod.operation = 'DIFFERENCE'        
                bool_mod.double_threshold=0    
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bool_mod.name)
                
                #remove redundant geometry 
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete(type='FACE') 
            
                #selecting border vertices
                mats=bpy.context.active_object.matrix_world
                OBJsurf.vertex_groups.active_index=vg.index
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.select_all(action='INVERT')
                self.manifold_surf=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
                
                #expanding selection to linked and ading verts to group        
                bpy.ops.mesh.select_linked(delimit={'SHARP'})
                bpy.ops.mesh.select_less()
                self.normal_surf=[mats*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
                bpy.ops.mesh.select_all(action='DESELECT')   
                
                #reselecting border vertices
                for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts:
                    if mats*i.co in self.manifold_surf:
                        i.select=True
                
                #clearing cage mesh
                bpy.data.objects.remove(OBJcage, True)     
                #cleared cage mesh
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                    
                 #removing redundant vertex group
                vg_old = OBJsurf.vertex_groups.get('Normal_Transfer')
                if vg_old is not None:
                    OBJsurf.vertex_groups.remove(vg_old)    
                    
                #adding internal surface verts to vg
                bpy.context.scene.objects.active=OBJvect
                OBJvect.select=True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.reveal()   
                
                verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]     
                vg = bpy.context.active_object.vertex_groups.new(name="Normal_Transfer")
                vgname=vg.name
                bpy.ops.object.mode_set(mode='OBJECT')
                vg.add(verts, 1.0, 'ADD') 
                bpy.ops.object.mode_set(mode='EDIT')
                
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_non_manifold()
                #revealing and merging meshes
                bpy.ops.object.mode_set(mode='OBJECT')
                OBJ_source=bpy.data.objects[self.OBJsource_NAME]
                bpy.ops.object.select_all(action='DESELECT') 
                OBJvect.select=True
                OBJsurf.select=True
                bpy.context.scene.objects.active=OBJsurf
                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode='EDIT')   
                
                #adding selected to vg and filling gap 
                verts = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select or mats*i.co in self.normal_surf]      
                vg = bpy.context.active_object.vertex_groups[vgname]
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.fill()
                
                bpy.ops.object.mode_set(mode='OBJECT') 
                vg.add(verts, 1.0, 'ADD')     
                
                bpy.ops.object.mode_set(mode='OBJECT')
                mod_DataTransfer = bpy.context.active_object.modifiers.new("DATATRANSFER", 'DATA_TRANSFER')
                mod_DataTransfer.object=OBJ_source
                mod_DataTransfer.use_loop_data=True
                mod_DataTransfer.data_types_loops={'CUSTOM_NORMAL'} 
                mod_DataTransfer.loop_mapping = 'POLYINTERP_NEAREST'
                mod_DataTransfer.vertex_group = vg.name          
                if smooth:      
                    bpy.ops.object.shade_smooth()
                    bpy.context.active_object.data.use_auto_smooth = 1
                    bpy.context.active_object.data.auto_smooth_angle=180 
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod_DataTransfer.name)
                OBJ_source.hide=False
                bpy.data.objects.remove(OBJ_source, True)           
                self.phase=6
                
            if self.phase==1: 
                bpy.ops.mesh.select_mode(type="VERT")               
                self.first_mouse_x = event.mouse_x            
                self.face_selected_indices = [i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]               
                bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
                self.selected = [i for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
                self.face_selected = [i for i in bmesh.from_edit_mesh(bpy.context.active_object.data).faces if i.select]                
                if len(self.face_selected)>0:
                    self.avg_normal=self.face_selected[0].normal-self.face_selected[0].normal
                    for f in self.face_selected:
                        self.avg_normal=self.avg_normal+f.normal
                    self.avg_normal=self.avg_normal/len(self.face_selected)
                self.phase=2    
            
                
        if event.type in {'RIGHTMOUSE', 'ESC', 'TAB'}:            
            return{'CANCELLED'} 
            self.phase=1
                
        if event.type =='ESC':
            return{'CANCELLED'} 
        return {'PASS_THROUGH'}
    
    def invoke(self,context,event):   
        if len(bpy.context.selected_objects)==2 and bpy.context.active_object.mode=='OBJECT':
            #bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
            self.first_mouse_x = event.mouse_x  
            OBJsurf=bpy.context.scene.objects.active
            OBJvect=bpy.context.selected_objects[0]
            self.OB_NAME=OBJvect.name
            if OBJsurf==OBJvect:
                OBJvect=bpy.context.selected_objects[1]
            self.OBJsurf_NAME=OBJsurf.name
            self.OBJvect_NAME=OBJvect.name          
            mod_shrinkwrap = OBJvect.modifiers.new("Temp_Shrinkwrap", 'SHRINKWRAP')        
            mod_shrinkwrap.target=OBJsurf                        
            #create duplicate normal source            
            OBJsource=OBJsurf.copy()
            OBJsource.data = OBJsurf.data.copy()
            bpy.context.scene.objects.link(OBJsource)
            self.OBJsource_NAME=OBJsource.name
            OBJsource.hide=True
            bpy.ops.object.select_all(action='DESELECT')
            fillvect(OBJvect)        
            OBJvect.select=True
            bpy.context.scene.objects.active=OBJvect
            bpy.ops.object.modifier_apply(modifier=mod_shrinkwrap.name)
            thick=(((OBJsurf.dimensions[0]+OBJvect.dimensions[0])/2+(OBJsurf.dimensions[1]+OBJvect.dimensions[1])/2+(OBJsurf.dimensions[2]+OBJvect.dimensions[2])/2)/3)/10          
            OBJcage=makecage(OBJvect,thick) 
            self.OBJcage_NAME=OBJcage.name
            self.sens_multi=((OBJcage.dimensions[0]+OBJcage.dimensions[1]+OBJcage.dimensions[2])/3)*10
            
            #Finding manifold verts fo further manipulation
            bpy.ops.object.select_all(action='DESELECT')    
            OBJvect.select=True
            bpy.context.scene.objects.active=OBJvect
            OBJsurf.hide=True
            bpy.ops.object.mode_set(mode='EDIT')              
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            vmat=OBJvect.matrix_world
            self.manifold_vect = [vmat*i.co for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]     
            #Finished finding manifolds        
            
            bpy.ops.mesh.select_all(action='SELECT')  
            bpy.ops.mesh.inset(thickness=0)
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, context.window)
            wm.modal_handler_add(self)       
            return {'RUNNING_MODAL'}
        else:
            return {'FINISHED'}

class jwcarvermenu(bpy.types.Menu):
    bl_label="Engraver"
    bl_idname="jw.carvermenu"    
    def draw(self,context):
        layout=self.layout
        layout.operator_context = "INVOKE_DEFAULT";
        layout.operator(jwinsertoperator.bl_idname)
        layout.operator(jwcarveoperator.bl_idname)    
        layout.operator(jwcutoperator.bl_idname)    
        layout.menu(jwbooleans.bl_idname)
        layout.menu(jwmirrors.bl_idname)
        layout.menu(jwsettings.bl_idname) 

addon_keymaps = []

def register():
    bpy.utils.register_class(jwsettings)   
    bpy.utils.register_class(jwcutoperator)   
    bpy.utils.register_class(jwcarveoperator)   
    bpy.utils.register_class(jwcarvermenu)
    bpy.utils.register_class(jwinsertoperator)
    bpy.utils.register_class(jwbooleans)
    bpy.utils.register_class(jwbooldiff)
    bpy.utils.register_class(jwboolunion)
    bpy.utils.register_class(jwboolintersect)
    bpy.utils.register_class(jwmirrors)
    bpy.utils.register_class(jwmirrorx)
    bpy.utils.register_class(jwmirrory)
    bpy.utils.register_class(jwmirrorz)
    bpy.types.Scene.axis_enum = bpy.props.EnumProperty(
        name = "Axis",
        description = "choose axis",
        items = [
            ("X" , "X" , "X axis"),
            ("Y", "Y", "Y axis"),
            ("Z", "Z", "Z axis"),
        ]
    )
    bpy.types.Scene.depth_prop = bpy.props.FloatProperty(name="Depth",default=0.2,step=0.001)
    wm = bpy.context.window_manager
    km=wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi=km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', ctrl=False, shift=False, alt=True)
    kmi.properties.name=jwcarvermenu.bl_idname
    #kmi=km.keymap_items.new(jwcarveoperator.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
    #bpy.ops.wm.call_menu(name="jw.carvermenu")
    addon_keymaps.append(km)

def unregister():    
    bpy.utils.unregister_class(jwsettings)
    bpy.utils.unregister_class(jwcutoperator)
    bpy.utils.unregister_class(jwcarveoperator)
    bpy.utils.unregister_class(jwcarvermenu)
    bpy.utils.unregister_class(jwinsertoperator)
    bpy.utils.unregister_class(jwbooleans)
    bpy.utils.unregister_class(jwbooldiff)
    bpy.utils.unregister_class(jwboolunion)
    bpy.utils.unregister_class(jwboolintersect)   
    bpy.utils.unregister_class(jwmirrors)
    bpy.utils.unregister_class(jwmirrorx)  
    bpy.utils.unregister_class(jwmirrory)  
    bpy.utils.unregister_class(jwmirrorz)  
    del bpy.types.Scene.axis_enum 
    del bpy.types.Scene.depth_prop  
    km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()

#bpy.ops.jw.carve('INVOKE_DEFAULT')