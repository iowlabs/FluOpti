/*
    With this code you can make a camera holder for RPI camera from waveshare (http://www.waveshare.com/product/mini-pc/raspberry-pi/cameras/rpi-camera-b.htm) or for V2 RPI camera (https://www.raspberrypi.org/products/camera-module-v2/)
    
    The code was modified from Fernán Federici 2017 version.
    
    This is licensed under the Creative Commons - Attribution license (CC BY 4.0)
    Isaac Núñez 2020.
 
*/

///////////////////////
// Fluopi parameters

holder_x=54;//acrylic bed width to fit into holder
holder_z=3*1.1;//acrylic bed thickness to fit into holder, normally 3 mm acrylic. 1.1 correction factor applied to surpass acrylic manufacture variations.

holder_y =41; // acrylic bed deep not inserted into the holder. It is equal to the distance between the holder and the enclosure wall. 

plate_center= 66; //distance from the enclosure wall to the center of the plate.

// LED ring parameters

r_ext = 70/2; // external radius
r_int = 40/2; // internal radius
ring_h = 1.5; // PCB height
r_sh = 1.5; // screw holes radius
x_shd = 60; // screw holes x distance
y_shd = 23; // screw holes y distance
LED_z = 8; // LEDs height

CCFB = plate_center - holder_y; // Camera Center From Border

////////////////////////
// Defined by the user

// ** camera holder parameters ** 

side_thick = 2; //side support thickness
bottom_thick = 1; // bottom support thickness
back_thick = 2; // back support thickness

sup_x_error = 0.5; // camera support error in x axis.

// ** Base holder parameters **

sca_thick_up = 3; // holder scafold thickness
sca_thick_side = 3; // holder scafold thickness
sca_thick_down = 2; // holder scafold thickness
sca_deep = 14;  // holder scafold back deep, it have to be shorter than the distance to the screws in the camera PCB (14 mm aprox) plus camera hoder "back_thick" parameter. We use 10 for WS and HQ camera.
sca_arms_width = 11; // holder scafold arms width

sca_arms_space_x = 1;  // space attach relaxation in x axis
sca_arms_space_y = 10;  // space attach relaxation in y axis (deep of the space)

ts_x = 10; // triangular supports x size
ts_y = 7;  // triangular supports y size

sca_trans = (sca_thick_up - sca_thick_down)/2; // translate the holder space to achieve the desired up and down thicknes

scafold_x = holder_x + 2*sca_thick_side;
scafold_y = plate_center + back_thick - holder_y; // depth
scafold_z = holder_z + sca_thick_up + sca_thick_down;

// ** LED ring holder and arms parameters **

// for the ring holder support
hrh_y = 2; // hole border y thickness
hrh_z = 2.5; // hole border z thickness

rh_screw = 1.5; // ring holder-arms screw radius

// for the arms
arm_z = 15; // arm z lenght
arm_tick = 3; // arm thickness

arm_hbt = 2.5; // hole borders thickness
ra_screw = 1.5; // ringholder-arms screw rad
s_arm_screw = 1.5; // arms screw hole separation from scafold.

// for the ring enclosure
re_zt = 2; // ring enclosure z thickness
re_rt = 2; // ring enclosure r thickness
re_scw = 1.5; //screw supports thickness
re_rfe = 2; // ring enclosure r free space  (between the PCB and external enclosure in r axis)
re_rfei = 1; // ring enclosure r free space internal hole (between the PCB and internal enclosure in r axis)

re_fh = 18.5; // front height. This is the LED height after having soldered them
re_dh = 3; // difussor separation from LEDs 
re_bh = 4; // back heigh. Left some air space equivalent to the screw support lenght
chs_x = 3; // cable hole space in x axis
chs_z = 3; // cable hole space in z axis. This value is added over the clamp height

re_cd = 1; // clamp deep
re_cw = 4; // clamp wide
re_ch = 2; // clamp height
re_cdh = re_cd + 0.3; // clamp deep hole, 0.3 looseness 
re_cw1 = re_cw + 0.5; // clamp wide 1st section, 1 looseness
re_cw2 = 2.5*re_cw1; // clamp wide 2nd section
re_ch1 = 2; // clamp height 1st section
re_ch2 = re_ch + 1; // clamp height 2nd section, 1 looseness


hre = re_dh + re_fh + ring_h +re_bh + re_zt ; // ring enclosure heigh
rre = r_ext + re_rfe + re_rt;//ring enclosure radius
rrei = r_int-re_rfei;// ring enclosure internal radius

//for the diffusor holder
dh_zt = 2; // difusor holder z thickness
dh_sheet = 2.5; // external difusor holder sheet in r axis to support the difussor.

dhi_sheet = 1; // inner difusor holder sheet in r axis to support the difussor.
dhi_h = 0; // inner border height
dhi_rt = 1; // inner diffusor holder tickiness in r axis.

/////////////////////
//  Camera details:

////////////////////////////////
// Waveshare Chinesse camera //
///////////////////////////////
waveshare_cam_x=32.2; // 1mm of error
waveshare_cam_y=32.2; 
waveshare_cam_z=1.5*1.1;//thickness
WS_hold_x = 5.1 - 0.3;    // space between border and cable conector. 0.3 the security factor
WS_hold_y = 4.5 - 0.3;  // space between border and resistor. 0.3 the security factor
WS_lens_y = waveshare_cam_y/2; // distance of the center of the lens to the bottom of the PCB (the side where cable is conected)

WS_scw_r = 1.5/2;   // camera screw radious
WS_scw_b = 2;  // distance from bottom to screw hole center
WS_scw_s = 2; // distance from side to screw hole center

///////////////////
// RPI V2 camera //
///////////////////

RPIV2_cam_x = 25 ; // PCB size in x axis
RPIV2_cam_y = 24; 
RPIV2_cam_z = 1 + 0.1; // PCB thickness, 0.1 mm of error


RPIV2_sensor_x = 8.5 + 0.5; // sensor base length (8.5 mm) or adaptor lenght + 0.5 mm error. For some reason use 16.
RPIV2_sensor_y = 8.5; //
RPIV2_sensor_bottom = 5; // distance from sensor square to PCB bottom (the side with the cable)

V2_hold_x =(RPIV2_cam_x - RPIV2_sensor_x)/2 - 0.3;    // space between camera border and sensor base. 0.3 the security factor
V2_hold_y = 12.5 - 0.2;  // space between border and PCB first obstacle (sensor base or electronic componentes). 0.2 security value. Use value = 12.5 to attach with screws or 7 to not use them.
V2_lens_y = RPIV2_sensor_y/2 + RPIV2_sensor_bottom; // distance of the center of the lens to the bottom of the PCB (the side with the cable)

V2_scw_r = 1;   // camera screw radious (M2)
V2_scw_b = 9.2;  // distance from bottom to screw hole center
V2_scw_s = 1.75; // distance from side to screw hole center.
V2_scw_f = 2; // distance from front (opposite side of the cable connector) to screw hole center

V2_cch = 2.8; // cable conector thickness
V2_ccx = 22; // cable conector wide (x axis)
V2_ccy = 5.6 + 0.2; // cable conector deep (y axis). 0.2 looseness.

V2_iss = 16; // inter screw free space in x axis (It has to be free for PCB componentes).

///////////////////
// RPI HQ camera //
///////////////////

HQ_cam_x = 38; // wide
HQ_cam_y = 38;  // deep
HQ_cam_z = 1.5; // PCB thickness

r_scw_adapt = 1; // Screw hole adaptor for M2 screws

HQ_hold_x = 7.2 - 0.3;    // space between border and camera base. 0.3 the security factor
HQ_hold_y = 7.3 - 0.3;  // space between border and first resistor. 0.3 the security factor
HQ_lens_y = HQ_cam_y/2; // distance of the center of the lens to the bottom of the PCB (the side where cable is conected)

HQ_scw_r = 2.5/2;   // camera screw radious (M2.5)
HQ_scw_b = 2.5 + HQ_scw_r ;  // distance from bottom to screw hole center
HQ_scw_s = 2.5 + HQ_scw_r; // distance from side to screw hole center    

HQ_blr = 35/2; //Lens base radious in the PCB
HQ_cch = 2.5; // cable conector heigh

module make_chb(scw_r,scw_y,screw_x,scafold_y, LRS){
    // to make the camera holder base inside the camera_holder_base module
    union(){
    difference(){
        // base parallelepiped
        cube([scafold_x,scafold_y,scafold_z], center=true);
        // internal hole for acrylic arms
        translate([0,0,sca_trans])
        cube([holder_x,scafold_y*1.1,holder_z], center=true);
        // central square down hole
        translate([0,sca_deep/2,scafold_z-holder_z])
        difference(){
            cube([scafold_x - 2*sca_arms_width,scafold_y - sca_deep,scafold_z], center=true);
        // triangular support left
            translate([-scafold_x/2 + sca_arms_width,(-scafold_y + sca_deep)/2,0])
            linear_extrude(height = scafold_x - 2*sca_arms_width, center = true, convexity = 10, twist = 0)
            polygon(points=[[0,0],[0,ts_y],[ts_x,0]]);
            // triangular support right
            mirror([1,0,0])translate([-scafold_x/2 + sca_arms_width,(-scafold_y + sca_deep)/2,0])
            linear_extrude(height = scafold_x - 2*sca_arms_width, center = true, convexity = 10, twist = 0)
            polygon(points=[[0,0],[0,ts_y],[ts_x,0]]);
        }
        
        // central square up hole
        translate([0,sca_deep/2,-scafold_z+holder_z])
        difference(){
            cube([scafold_x - 2*sca_arms_width,scafold_y - sca_deep,scafold_z], center=true);
            // triangular support left
            translate([-scafold_x/2 + sca_arms_width,(-scafold_y + sca_deep)/2,0])
            linear_extrude(height = scafold_x - 2*sca_arms_width, center = true, convexity = 10, twist = 0)
            polygon(points=[[0,0],[0,ts_y],[ts_x,0]]);
            // triangular support right
            mirror([1,0,0])translate([-scafold_x/2 + sca_arms_width,(-scafold_y + sca_deep)/2,0])
            linear_extrude(height = scafold_x - 2*sca_arms_width, center = true, convexity = 10, twist = 0)
            polygon(points=[[0,0],[0,ts_y],[ts_x,0]]);
        }
        
        // attach arms holes
        hole_x = holder_x/2-sca_arms_space_x/2;
        for (a =[hole_x,-hole_x]){
            translate([a,(scafold_y-sca_arms_space_y)/2,scafold_z/2])
            cube([sca_arms_space_x,sca_arms_space_y,scafold_z], center=true);
        }
        
        // screw holes
        scw_h = sca_thick_down; 
        
        for (a =[screw_x,-screw_x]){
            translate([a,-scafold_y/2+scw_y,(scafold_z-scw_h)/2])
        //(scafold_z-scw_h)/2
            cylinder(h=scw_h, r=scw_r, $fn                  =120, center =true);
        }
    }
     
    if(LRS == 1){
        translate([scafold_x/2,scafold_y/2-CCFB,scafold_z/2])
        led_ring_support();
        
        mirror([1,0,0])
        translate([scafold_x/2,scafold_y/2-CCFB,scafold_z/2])
        led_ring_support();
        
        }
    }
}


module cam_holder_base(camera, LRS) {
    // it creates the camera holder base based on the specified camera
    
    if(camera == "waveshare"){
        cam_x = waveshare_cam_x;
        cam_y = waveshare_cam_y;
        scw_x = WS_scw_s + side_thick;
        scw_y = WS_scw_b + back_thick;
        scw_r = WS_scw_r;
    
        support_x = cam_x+2*side_thick; 
        screw_x = support_x/2-scw_r-                  scw_x;
        
        scafold_y = scafold_y + WS_lens_y; //increase scafold deep accord distance of the lens in the PCB
    
        make_chb(scw_r,scw_y,screw_x,                 scafold_y, LRS);
        }
    
    else if(camera == "RPIHQ"){
        cam_x = HQ_cam_x;
        cam_y = HQ_cam_y;
        scw_x = HQ_scw_s + side_thick;
        scw_y = HQ_scw_b + back_thick;
        scw_r = r_scw_adapt; // intead of HQ_scw_r as we dont have the screws
        
        //support_y = HQ_hold_y + back_thick;
        support_x = cam_x+2*side_thick; 
        screw_x = cam_x/2-HQ_scw_s;
        
        scafold_y = scafold_y + HQ_lens_y;
        make_chb(scw_r,scw_y,screw_x,                 scafold_y, LRS);
    
        }
    
    else if(camera == "RPIV2"){
        cam_x = RPIV2_cam_x;
        cam_y = RPIV2_cam_y;
        scw_x = V2_scw_s + side_thick;
        scw_y = V2_scw_b + back_thick;
        scw_r = V2_scw_r;
    
        support_x = cam_x+2*side_thick; 
        screw_x = cam_x/2-V2_scw_s;
        
        scafold_y = scafold_y + V2_lens_y;
        //increase scafold deep accord distance of the lens in the PCB
        make_chb(scw_r,scw_y,screw_x,                 scafold_y, LRS);
    
        }
     
}

module camera_mount(camera){
    // it creates the camera mount over the base holder, based on the specified camera.
    
    
    if(camera == "waveshare"){
            cam_x = waveshare_cam_x;
            cam_y = waveshare_cam_y;
            cam_z = waveshare_cam_z;
            hold_x = WS_hold_x;
            hold_y = WS_hold_y;
            scw_y = WS_scw_b + back_thick;
            scw_x = WS_scw_s + side_thick;
            scw_r = WS_scw_r;
        
        scafold_y = scafold_y + WS_lens_y;
        
        support_z = cam_z+bottom_thick;
        support_y = hold_y + back_thick;
        support_x = cam_x+2*side_thick+sup_x_error; 
        
        
        translate([0,(support_y-scafold_y)/2,scafold_z/2+support_z/2])
        difference(){
            //Base parallelepiped
            cube([support_x,support_y,support_z], center=true);
            //camera space
            translate([0,back_thick/2,-bottom_thick/2])
            cube([cam_x+sup_x_error,hold_y,cam_z], center=true);
            //cable connector space
            cube([cam_x - 2*hold_x,support_y,support_z], center=true);
            
            //Screw holes
            screw_x = support_x/2-scw_r-scw_x;
            for (a =[screw_x,-screw_x]){
                translate([a,-support_y/2+scw_r+scw_y ,0])
                cylinder(h=support_z, r=scw_r, $fn=120, center =true);
                }            
        }    
    }
    
    else if(camera == "RPIHQ"){
            cam_x = HQ_cam_x;
            cam_y = HQ_cam_y;
            cam_z = HQ_cam_z;
            hold_x = HQ_hold_x;
            hold_y = HQ_hold_y;
            scw_y = HQ_scw_b + back_thick;
            scw_x = HQ_scw_s + side_thick;
            scw_r = HQ_scw_r;
        
        scafold_y = scafold_y + HQ_lens_y;
        
        support_z = cam_z+HQ_cch;
        support_y = hold_y + back_thick;
        support_x = cam_x+2*side_thick+sup_x_error; 
        
        //screw_x = support_x/2-scw_r-scw_x;
        screw_x = cam_x/2-HQ_scw_s;
        
        translate([0,(support_y-scafold_y)/2,scafold_z/2+support_z/2+HQ_cch])
        union(){
            //camera PCB frame
            difference(){
                //Base parallelepiped
                translate([0,0,-HQ_cch])
                cube([support_x,support_y,support_z], center=true);
                //camera space
                translate([0,back_thick/2,0])
                cube([cam_x+sup_x_error,hold_y,support_z], center=true);
                //cable conector space
                translate([0,0,-HQ_cch]) 
                cube([cam_x - 2*hold_x,support_y,support_z], center=true);
                //Screw holes
                for (a =[screw_x,-screw_x]){
                    translate([a,-support_y/2+scw_y, -HQ_cch])
                    cylinder(h=3*support_z, r=r_scw_adapt, $fn=120, center =true);
                }
            }
            /*/
            //Screw hole adaptors
            for (a =[screw_x,-screw_x]){
                translate([a,-support_y/2+scw_y ,(cam_z-support_z)/2])
                difference(){
                    // to enter in PCB holes
                    cylinder(h=cam_z, r=scw_r, $fn=120, center =true);
                    // to make M2 holes
                    cylinder(h=cam_z, r=r_scw_adapt, $fn=120, center =true);     
                }
        
            }
            */
        }    
    }
    
    else if(camera == "RPIV2"){
            cam_x = RPIV2_cam_x;
            cam_y = RPIV2_cam_y;
            cam_z = RPIV2_cam_z;
            hold_x = V2_hold_x;
            hold_y = V2_hold_y;
            base_space = V2_ccx +0.2;
            scw_y = V2_scw_b + back_thick;
            scw_x = V2_scw_s + side_thick;
            scw_r = V2_scw_r;
        
        scafold_y = scafold_y + V2_lens_y;
        
        support_z = cam_z+bottom_thick + V2_cch;
        support_y = hold_y + back_thick;
        support_x = cam_x+2*side_thick +sup_x_error;
        
        sfs_ccy = V2_ccy + back_thick; //support free space for cable conector in y axis.
        screw_x = cam_x/2-V2_scw_s;
        //
        translate([0,(support_y-scafold_y)/2,scafold_z/2+support_z/2+V2_cch])
        union(){
            //camera PCB frame
            difference(){
                //Base parallelepiped
                translate([0,0,-V2_cch])
                cube([support_x,support_y,support_z], center=true);
                //camera space
                translate([0,back_thick/2,0])
                cube([cam_x+sup_x_error,hold_y,support_z], center=true);
                //cable conector space
                translate([0,(sfs_ccy-support_y)/2,-V2_cch]) 
                cube([base_space,sfs_ccy,support_z], center=true);
                //inter screw space
                translate([0,(sfs_ccy)/2,-V2_cch]) 
                cube([V2_iss,support_y -sfs_ccy,support_z], center=true);
                
                //Screw holes
                for (a =[screw_x,-screw_x]){
                    translate([a,-support_y/2+scw_y, -V2_cch])
                    cylinder(h=3*support_z, r=r_scw_adapt, $fn=120, center =true);
                }
            }
        }
    //
    }
    
}

module led_ring_support(){
    //  it creates the support for the LED ring.
    
    lrs_x = sca_thick_side;
    lrs_y = 2 * hrh_y + rh_screw;
    lrs_z = 2 * hrh_z + rh_screw;
    
    translate([-lrs_x/2,0,lrs_z/2])
    union(){
        difference(){
            //base cube with screw hole
            cube([lrs_x,lrs_y,lrs_z], center=true);
            rotate([0,90,0]) 
            cylinder($fn = 50, h=sca_thick_side, r=rh_screw, center=true);
        }
        // triangular support back
        translate([0,lrs_y/2,-lrs_z/2])
        rotate([0,-90,0]) 
        linear_extrude(height = lrs_x, center = true, convexity = 10, twist = 0)
        polygon(points=[[0,0],[0,lrs_z/2],[lrs_z,0]]);
    
        // triangular support front
        mirror([0,1,0])translate([0,lrs_y/2,-lrs_z/2])
        rotate([0,-90,0]) 
        linear_extrude(height = lrs_x, center = true, convexity = 10, twist = 0)
        polygon(points=[[0,0],[0,lrs_z/2],[lrs_z,0]]);
    }        
    
}

module led_ring_enclosure(){
    // to create the PCB ring enclosure
        
    difference(){
        union(){
            // base cylinder
            difference(){
            cylinder($fn = 100, h=hre, r=rre, center=true);
            translate([0,0,re_zt/2])
            cylinder($fn = 100, h=hre-re_zt, r=rre-re_rt, center=true);
            }
            
            // internal cylinder
            cylinder($fn = 100, h=hre, r=rrei, center=true);
            
            //screw supports
            for (x =[x_shd/2,-x_shd/2]){
                for (y =[y_shd/2,-y_shd/2]){ 
                    translate([x,y,(re_bh-hre)/2+re_zt])
                    cylinder($fn = 100, h=re_bh, r=rh_screw + r_sh, center=true);
                }
            }
        }
            //internal hole
            cylinder($fn = 100, h=hre, r=rrei-re_rt, center=true);
            
            //screw holes for LED ring
            for (x =[x_shd/2,-x_shd/2]){
                for (y =[y_shd/2,-y_shd/2]){ 
                    translate([x,y,(re_bh-hre+re_zt)/2])
                    cylinder($fn = 100, h=re_bh+re_zt, r=r_sh, center=true);
                }
            }
            
            //cable hole
            chsz_final = chs_z + re_ch1 + re_ch2;
            translate([0,rre-0.5*re_rt,(hre-chsz_final)/2])
            cube([chs_x,2*re_rt,chsz_final], center = true);
            
            //arms hole
            xash = scafold_x/2 + arm_tick + s_arm_screw+ra_screw;
            
            for (x =[xash,-xash]){
                translate([x,0,(re_zt-hre)/2])
                cylinder($fn = 100, h=re_zt, r=ra_screw, center=true);
                }
            
            // Clamp
            for (rc =[rre-re_cdh,-(rre)]){
                
                // enter track
                c_angle1 = (re_cw1/(rre - re_cdh))*360/(2*PI);
                translate([0,0,hre/2-re_ch1])
                rotate_extrude(angle = c_angle1,convexity = 5, $fn = 500)
                translate([rc,0,0])
                polygon( points=[[0,0],[0,re_ch1],[re_cdh,re_ch1],[re_cdh,0]] );
                
                // horizontal track
                c_angle2 = (re_cw2/(rre - re_cdh))*360/(2*PI);
                translate([0,0,hre/2-(re_ch1+re_ch2)])
                rotate_extrude(angle = c_angle2,convexity = 5, $fn = 500)
                translate([rc,0,0])
                polygon( points=[[0,0],[0,re_ch2],[re_cdh,re_ch2],[re_cdh,0]] );
            }

    }
    
}
module led_ring_diffusor_out(){
    // to create the outer ring diffusor holder
    
    lrd_h = dh_zt + re_ch1 + re_ch2;
    lrd_r = rre+re_rt+0.3; // 0.3 looseness
    
    rotate([180,0,0])
    union(){
        difference(){
            //base cylinder
            cylinder($fn = 100, h=lrd_h, r=lrd_r, center=true);
            
            //central hole
            translate([0,0,dh_zt/2])
            cylinder($fn = 100, h=lrd_h-dh_zt, r=lrd_r-re_rt, center=true);
            //diffusor support sheet
            cylinder($fn = 100, h=lrd_h, r=lrd_r-re_rt-dh_zt, center=true);    
        }
        
        // clamp
        for (rc =[lrd_r-re_rt-re_cd,-(lrd_r-re_rt)]){
            c_angle = (re_cw/(lrd_r - re_cd))*360/(2*PI);
            translate([0,0,lrd_h/2-re_ch])
            rotate_extrude(angle = c_angle,convexity = 5, $fn = 500)
            translate([rc,0,0])
            polygon( points=[[0,0],[0,re_ch],[re_cd,re_ch],[re_cd,0]] );
        }
    }
    
}

module led_ring_diffusor_in(){
    // To create the inner ring to support the diffusor
    in_corr = 0.1;// internal hole radius looseness
    rchole = rrei + in_corr; // corrected internal hole radius
    
    rotate([180,0,0])
    difference(){
        //base cylinder
        cylinder($fn = 100, h=dhi_h+dh_zt, r=rchole+dhi_rt+dhi_sheet, center=true);
        //central hole
        cylinder($fn = 100, h=dhi_h+dh_zt, r=rchole+in_corr, center=true);
        //diffusor support sheet
        translate([0,0,dh_zt/2])
        difference(){
            cylinder($fn = 100, h=dhi_h, r=rchole+dhi_rt+dhi_sheet, center=true);
            cylinder($fn = 100, h=dhi_h, r=rchole+dhi_rt, center=true);
        }    
    }
    
    
}

module led_ring_arms(){
    // To create the arms to attach the led ring enclosure to the camera support
    arm_y = 2*(arm_hbt + rh_screw);
    
    rotate([180,0,0]) // to display
    union(){
        
        // vertical portion
        translate([arm_tick/2,0,arm_z/2])
        difference(){
            cube([arm_tick,arm_y,arm_z], center=true);
            cube([arm_tick,2*rh_screw,arm_z-2*arm_tick], center=true);
        }
        
        //horizontal portion
        difference(){
            arm_x = arm_hbt + 2*ra_screw +    s_arm_screw+arm_tick;
            translate([arm_x/2,0,arm_tick/2])
            cube([arm_x,arm_y,arm_tick], center = true);
            translate([ra_screw+s_arm_screw+arm_tick,0,arm_tick/2])
            cylinder($fn = 100, h=arm_tick, r=ra_screw, center=true);
        }
    }
}

module led_ring(camera){
    
    // it is necessary to indicate the camera to position the ring LED properly (aligned with lent)
    if(camera == "waveshare"){
        
        cam_y = waveshare_cam_y;
        scafold_y = scafold_y + cam_y/2;
        
    translate([0,scafold_y/2-CCFB,arm_z])
    difference(){
        cylinder(h=ring_h, r=r_ext, center=true);
        cylinder(h=ring_h, r=r_int, center=true);
        }
    }
    
    else if(camera == "RPIV2"){
        
        cam_y = RPIV2_cam_y;
        scafold_y = scafold_y + cam_y/2;
        
    translate([0,scafold_y/2-CCFB,arm_z])
    difference(){
        cylinder(h=ring_h, r=r_ext, center=true);
        cylinder(h=ring_h, r=r_int, center=true);
        }
    }

}

module display_camera(camera){
    lcr = 2; // radius of the cylinder to indicate the center of the lens
    
    if(camera == "waveshare"){
        
        cam_x = waveshare_cam_x;
        cam_y = waveshare_cam_y;
        cam_z = waveshare_cam_z;
        scw_x = WS_scw_s + side_thick;
        scw_y = WS_scw_b + back_thick;
        scw_r = WS_scw_r;
        
        support_x = cam_x+2*side_thick; 
        screw_x = support_x/2-scw_r-                  scw_x;
        scafold_y = scafold_y + cam_y/2;
        
        translate([0,(cam_y-scafold_y)/2+ back_thick,(cam_z+scafold_z)/2])
        union(){
            // PCB
            cube([cam_x,cam_y,cam_z],center = true);
            //Lens center
            cylinder(h=2*cam_z, r=lcr, center=true);
            //translate([0,0,(scafold_z/2)+cam_z+2])
            //cube([1.5*scafold_x,1,1],center = true);
        }
    }
    else if(camera == "RPIHQ"){
        cam_x = HQ_cam_x;
        cam_y = HQ_cam_y;
        cam_z = HQ_cam_z;
        scw_x = HQ_scw_s + side_thick;
        scw_y = HQ_scw_b + back_thick;
        scw_r = HQ_scw_r;
        
        support_x = cam_x+2*side_thick; 
        screw_x = support_x/2-scw_r-                  scw_x;
        scafold_y = scafold_y + cam_y/2;
        
        translate([0,(cam_y-scafold_y)/2+ back_thick,(cam_z+scafold_z)/2+HQ_cch])
        union(){
            //PCB
            difference(){
                // base PCB
                cube([cam_x,cam_y,cam_z],center = true);
                //Screw holes
                for (sx =[cam_x/2-HQ_scw_s,HQ_scw_s-cam_x/2]){
                    for (sy =[cam_y/2-HQ_scw_b,HQ_scw_b-cam_y/2]){                    translate([sx,sy,0])               
                        cylinder(h=cam_z, r=scw_r, $fn=120, center =true);     
                        }
                }
            }
            // Lens Base in the PCB
            cylinder(h=2*cam_z, r=HQ_blr);
            //Lens center
            translate([0,0,cam_z])
            cylinder(h=4*cam_z, r=lcr, center =true);
            //cable connector
            translate([0,(HQ_hold_y-cam_y)/2,-(cam_z+HQ_cch)/2])
            cube([cam_x-2*(HQ_hold_x),HQ_hold_y,HQ_cch], center = true);
        }
        
    }
    
    
    else if(camera == "RPIV2"){
        cam_x = RPIV2_cam_x;
        cam_y = RPIV2_cam_y;
        cam_z = RPIV2_cam_z;
        scw_x = V2_scw_s + side_thick;
        scw_y = V2_scw_b + back_thick;
        scw_r = V2_scw_r;
        
        support_x = cam_x+2*side_thick; 
        screw_x = support_x/2-scw_r-                  scw_x;
        scafold_y = scafold_y + cam_y/2;
        
        translate([0,(cam_y-scafold_y)/2+ back_thick,(cam_z+scafold_z)/2])
        union(){
        //PCB
            difference(){
                // base PCB
                cube([cam_x,cam_y,cam_z],center = true);
                //Screw holes
                for (sx =[cam_x/2-V2_scw_s,V2_scw_s-cam_x/2]){
                    for (sy =[cam_y/2-V2_scw_f,V2_scw_b-cam_y/2]){                    translate([sx,sy,0])               
                        cylinder(h=cam_z, r=scw_r, $fn=120, center =true);     
                        }
                }
            }
            //Lens center
            translate([0,-cam_y/2+V2_lens_y,0])
            cylinder(h=2*cam_z, r=lcr, center=true);
            //cable connector
            translate([0,(V2_ccy-cam_y)/2,-(cam_z+V2_cch)/2])
            cube([V2_ccx,V2_ccy,V2_cch], center = true);
        }
    }
}

//uncomment the camera you pretend to use

//camera = "waveshare";
camera = "RPIV2";
//camera = "RPIHQ";
LRS = 1; // 1 to add LED Ring Support, 0 to don't.


//cam_holder_base(camera,LRS);
//camera_mount(camera);
//led_ring_diffusor_in();
/*
ztrans = hre/2+arm_z; 
translate([0,0,ztrans])
union(){
translate([scafold_x/2,0,-hre/2])
led_ring_arms();
led_ring_enclosure();
translate([0,0,hre/2+5])
    
union(){
    led_ring_diffusor_out();
    led_ring_diffusor_in();
    }
}
*/   
//uncomment next modules to display the elements
//display_camera(camera);
//led_ring(camera);

/*
union(){
    translate([0,12.5,-3.65])
    camera_mount(camera);
    cube([30,15,1], center=true);
    
    }
   */