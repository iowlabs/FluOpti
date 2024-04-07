/*

       This code is part of  a collaborative project between Lab Tecnologia Libre and IOWlabs 
    (c) Fernan Federici and Isaac Nuñez, 2022- Released under the CERN Open Hardware License   
*/

//include <picam_2_push_fit.scad>  
include </home/fernan/Documents/github/MiniFluOpti/hardware/Enclosure/Soportes camara/Flat_cam_holder.scad>  

//-------important parameters if you wish to change petri dish and  base dimensions below for customization

corr=0.2;// used to create extra fitting space for printing imperfections
petri_h=15;// petri dish height
petri_lid_d=92.4 + corr*3; //petri dish diameter, corr is added for extra space (e.g. parafilm)
LED_shield=40;//distance from illuminating hole to border used to hide the LEDs from the camera field of view



//-----------------secondary -parameters more unlikely to be changed

screw_d=21;//distance between screw holes in RPI camera holder
screw_r=2/2;//screw radius
screw_hold_r=2;
sensor_h=2; //space for sensor
sensor_x=8.5;//RPI camera sensor dim
wall_M12=1.5;
base_xy=16;
base_h=6;
M12_r=12/2;//radius of M12 lens
mount_h = 12;
wall=0.75;
holder_x=54;//acrylic bed width to fit into holder
holder_y=54;//acrylic bed thickness to fit into holder, normally 3mm acrylic
holder_z=3;//acrylic bed thickness to fit into holder, normally 3mm acrylic
h_ring= petri_h*2;//petri dish-holding ring 
light_box_h=50;
elastic_holder_dist=petri_lid_d+5;//petri_lid_d-8;// diameter of the illuminating hole, with a 4mm notch to hold the petri dish. It has to be smaller than petri_lid_d (Parkinson 2007 uses 82mm).


notch_y=11;
elastic_holder_xy=10;
elastic_holder_z=10;
M12_h=10;

PCB_optoLED_r=84/2;//how big is the ring from screw to screw
PCB_optoLED_r_ext=69/2;//external radius
PCB_optoLED_r_inte=41/2; //internal radius
PCB_LED_x=125;//155;// placa del FluOpti es de 15.5x11cm  y los agujeros estan a 3mm delos bordes en los dos ejes//
PCB_LED_y=81;//111;
diag=190; //diagonal of blue LED PCB (155 x 111)
cone_r=petri_lid_d/2*1.5;//bottom radius of cone
echo("cone r is", cone_r);

view_open_d=petri_lid_d-wall*4;
base_d=diag+wall*6;//diameter of printed light house cylinder
cone_r2=base_xy*2;//top radius
focus_h=40;
h_cam=90-h_ring;//height to camera 
inner_r=petri_lid_d*1.2/2;
velvet_background_ring_h=28;
LED_base_h=9;
LED_ring_ext_d=base_d-wall*3;
LED_ring_int_d=LED_ring_ext_d-10;
velvet_background_ring_d=LED_ring_int_d-wall*3;
velvet_background_ring_stage_r=velvet_background_ring_d/2-10;
inner_h=petri_h/2;
focus_r=cone_r2;
M13_neg_d=2.8;

wire_clearance_w=wall*7;
wire_clearance_x=wall*6;
wire_riel_h=focus_h*0.75;

raspi_z = 10;
raspi_board = [85, 58, 19]; // 3B model is 82*56*19.5mm and 4B is 88*58*19.5mm

//h = raspi_z + raspi_board[2] + 5;

echo(raspi_board[1]);

ITO_dim=100;
$fn=100;
    RG_ring_r=70/2;
    cone_r3=RG_ring_r+wall*8;
    
///////////////////////////
//// user defined values //
///////////////////////////
//r_inte = 48; // internal radius
//ri_thick = 1; // structure internal thickness
//re_thick_u = 3; // structure external thickness
//re_thick_d = 1; // structure external thickness
//z_thick = 2; // z structure thickness
//paper_space = 0.5; // space to fit the paper
//h_int = 3; // internal height where to fit paper
//

// for the arms
arm_z = 15; // arm z lenght
arm_tick = 3; // arm thickness

arm_hbt = 2.5; // hole borders thickness
ra_screw = 1.5; // ringholder-arms screw rad
s_arm_screw = 1.5; // arms screw hole separation from scafold.


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

//// external square support
//sq_x = 126;
//sq_y = 126;
//sq_thick = 2;

//c_hole_w = 3;  //cable hole wide
//c_hole_h = 3; //cable hole height
//b_dist = 6; // base support border distance, defined on the central axis
//b_thick = 2;
//base_h_sq = 15.8-sq_thick+z_thick;  // related to diffuser h

//x_displace = 3;  // hole displcement arround x axis

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
echo("rre is", rre);
 lrd_r = rre+re_rt+0.3;
echo("lrd_r is", lrd_r);
rrei = r_int-re_rfei;// ring enclosure internal radius



//// computed values
//r_ext_up = r_int+re_thick_u+ri_thick+paper_space;
//r_ext_down = r_int+re_thick_d+ri_thick+paper_space;
//h_total = h_int+z_thick;






//------------uncomment items below to render pieces--------------------------


//translate([ 0.00, 0.00, 330.00 ]) rotate([0,180.0]) camera_holder(type=1); //use type 1 for the RPI camera as it comes; type 2 and 3 use M12 but I need to update the thread libary (and use the same used in Saleroscope with Nano Castro) type 2 for M12 lens (removing the native RPIlens) using puh-fit approach from R. Bowman; type 3 is for M12lens but using screws to attach it to camera

//translate([ 0.00, 0.00, 150.00 ]) rotate([0,0,40]) cone_window_lid();  

//translate([ 0.00, 0.00, -150.00 ]) cone_hull_short();//usar este
//translate([ 0.00, 0.00, -150.00 ])  cone_hull();//de siempre

//translate([ 0.00, 0.00, 100.00 ]) extension_ring_long_v2();

//translate([ 0.00, 0.00, 55.00 ]) diffuser_holder(true);

//translate([ 0.00, 0.00, 0.00 ]) plate_holder();// .

//translate([ 0.00, 0.00, -80.00 ]) lighting_base();  
//lighting_base_squared();

//rotate([0,180,0])led_ring_enclosure();




//------------------------------------------------------------------------------------------------------

//led_ring_enclosure();
module led_ring_enclosure(){
    // to create the PCB ring enclosure
        
    difference(){
        union(){
            // base cylinder
            difference(){
            color("red")cylinder($fn = 100, h=hre, r=rre, center=true);
            translate([0,0,re_zt/2])
           color("white") cylinder($fn = 100, h=hre-re_zt, r=rre-re_rt, center=true);
            }
            
            // internal cylinder
            cylinder($fn = 100, h=hre, r=rrei, center=true);
            
            //screw supports
           color("red") for (x =[x_shd/2,-x_shd/2]){
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

module repeat(delta,N,center=false){ //repeat something along a regular array (from openflexure)
	translate( (center ?  -(N-1)/2 : 0) * delta)
				for(i=[0:1:(N-1)]) translate(i*delta) children();
}

module PCB_LED_support_frame(){
    // position supports for each of the pi's mounting screws
//    pi_frame() 
     repeat([PCB_LED_x-30,0,0],2,center=true) repeat([0,PCB_LED_y-30,0], 2, center=true) children();
}

// #  translate([0,0,-2]) PCB_LED_support();
module PCB_LED_support(){
    // pillars into which the pi can be screwed (holes are hollowed out later)
    difference(){
        PCB_LED_support_frame() cylinder(h=raspi_z, d=7, center=true);
        PCB_LED_support_frame() cylinder(h=raspi_z+2, d=M13_neg_d, center=true);
    }
}

//translate([ 0.00, 0.00, -80.00 ]) PCB_LED(); //just as a guide
module PCB_LED(){
    difference(){
    square([PCB_LED_x, PCB_LED_y], center=true);
      translate([0,0,-2])       PCB_LED_support_frame() cylinder(h=raspi_z+2, d=M13_neg_d, center=true);
}
    }
    
//     #  translate([0,0,10])        ITO();
    module ITO(){
            cube([ITO_dim+2, ITO_dim+2, h_ring*2], center=true);
        }

//RPI_holder();
module RPI_holder(){
    union(){
        pi_supports();
        cube([raspi_board[0]-20,raspi_board[1],2]);
    }
    }

module pi_support_frame(){
    // position supports for each of the pi's mounting screws
//    pi_frame() 
    translate([3.5,3.5]) repeat([raspi_board[1],0,0],2) repeat([0,49,0], 2) children();
}


module pi_supports(){
    // pillars into which the pi can be screwed (holes are hollowed out later)
    difference(){
        pi_support_frame() cylinder(h=raspi_z, d=7);
        pi_support_frame() cylinder(h=raspi_z+2, d=2.8);
    }
}




//cone_window_lid();
module cone_window_lid(){
      difference(){
                 translate([ 0.00, 0.00, focus_h/2 ]) color("red")  cylinder( r=cone_r3+wall*3, h=focus_h, center=true);
            translate([ 0.00, 0.00, focus_h/2 -wall*2 ]) color("blue")  cylinder( r=cone_r3+corr, h=focus_h-wall*2, center=true);
         translate([ 0.00, 0.00, focus_h/2 -wall*2 ]) color("cyan")  cylinder( r=focus_r-wall*8, h=focus_h+wall*1000, center=true);
            //operation window
          translate([ 0.00, 0.00, focus_h/2+wall*3]) minkowski(){ 
                    sphere(r=1.5); cube([ focus_r*3, focus_r, focus_h/2 ], center=true); }
}
    }
 

 int_top_cyl_r=lrd_r+wall;
roof_thick_h=10; //to screw holder and camera in

//translate([0,0,100]) top_part();                 
module top_part(){
    difference(){
       union(){
           //top camera square 
//           translate([ 0.00, 0.00, focus_h-mount_h/2+wall*3 ])    cube([base_xy+wall*3, base_xy+wall*3, mount_h], center = true);
      difference(){
                 translate([ 0.00, 0.00, focus_h/2+roof_thick_h/2 ]) color("green")  cylinder( r=int_top_cyl_r+wall*4, h=focus_h+wall*2+roof_thick_h, center=true);//
            translate([ 0.00, 0.00,focus_h/2-wall*2 ]) color("yellow")  cylinder( r=int_top_cyl_r+wall*2+corr   , h=focus_h-wall*2+corr, center=true);//corr was added in 2024 for prusa
//      translate([ 0.00, 0.00, focus_h+mount_h/2-corr ])     
//    color("Blue") cube([base_xy+corr*2, base_xy+corr*2, mount_h*20], center = true);
            //operation window
          translate([ 0.00, 0.00, focus_h/4]) rotate([0,0,90]) minkowski(){ 
                    sphere(r=1.5); cube([ focus_r*3, focus_r, focus_h/2 ], center=true); }
                  }}
//              color("green") cube([base_xy+corr*2, base_xy+corr*2, mount_h*300], center = true);
                
                  //wire clearance tunel
                  translate([int_top_cyl_r+wall*2-wall,0, focus_h/2-wall*2]) color("red")    cube([wire_clearance_x,wire_clearance_w+wall*4,focus_h+wall*2],center = true);
                  
                  //camera csi flat cable clearance
                     translate([int_top_cyl_r*2,0, focus_h+roof_thick_h-wall*3]) color("pink")    rotate([0,-9,0])cube([int_top_cyl_r*3,24,wall*3],center = true);
//                       translate([int_top_cyl_r*0.6,0, focus_h+roof_thick_h/2]) color("pink")    rotate([0,-7,0])cube([int_top_cyl_r*3,24,wall*3],center = true);
                  }            
     //cable riel
     difference(){
         translate([int_top_cyl_r+wall*2+wire_clearance_x/2-wall,0, focus_h/2-wall])     color("red")    cube([wire_clearance_x+wall*8,wire_clearance_w+wall*8,focus_h],center = true);
    translate([int_top_cyl_r+wall*2 +wire_clearance_x/2-wall,0, focus_h/2-wall*4])     color("blue")    cube([wire_clearance_x+wall*4+corr*2,wire_clearance_w+wall*3+corr*3,focus_h+corr],center = true);//the corr in wire_clearance_w is critical for tight fitting.
     
             translate([ 0.00, 0.00,focus_h/2-wall*2 ]) color("yellow")  cylinder( r=int_top_cyl_r+wall*2+corr   , h=focus_h-wall*2+corr, center=true);//corr was added in 2024 for prusa
       }
       
       //camera mount
          color("red")translate([ 0.00, 0.00, focus_h-wall*2+4])  rotate([0,180,90]) camera_mount(camera);
       
           //arms hole
//            xash = scafold_x/2 + arm_tick + s_arm_screw+ra_screw;
       xash=28;
           difference(){ 
               color("red")translate([ 0.00, 0.00, focus_h-wall*2])
       for (x =[xash,-xash]){
                translate([0,x,0])
                cylinder($fn = 100, h=20, r=ra_screw*3, center=true);
                }
           color("red")translate([ 0.00, 0.00, focus_h-wall*2])
       for (x =[xash,-xash]){
                translate([0,x,0])
                cylinder($fn = 100, h=20, r=ra_screw, center=true);
                }
            }
       
//    RG_PCB=[23,60]; //M3 screw positions
//LED_screw_h=raspi_z/2;
//                 
//  translate([ 0,0, focus_h-mount_h/2-LED_screw_h/2]) 
//    translate([0,0,0]) difference(){
//        union(){
//     translate([-RG_PCB[0]/2,-RG_PCB[1]/2,0])  cylinder(h=LED_screw_h, d=7, center=true);
//      translate([RG_PCB[0]/2,-RG_PCB[1]/2,0])  cylinder(h=LED_screw_h, d=7,  center=true);
//      translate([RG_PCB[0]/2,RG_PCB[1]/2,0])  cylinder(h=LED_screw_h, d=7,  center=true);
//      translate([-RG_PCB[0]/2,RG_PCB[1]/2,0])   cylinder(h=LED_screw_h, d=7,  center=true);  
//        } 
//          union(){
//     translate([-RG_PCB[0]/2,-RG_PCB[1]/2,-corr])  cylinder(h=LED_screw_h, d=2.8, center=true);
//      translate([RG_PCB[0]/2,-RG_PCB[1]/2,-corr])  cylinder(h=LED_screw_h, d=2.8,  center=true);
//      translate([RG_PCB[0]/2,RG_PCB[1]/2,-corr])  cylinder(h=LED_screw_h, d=2.8,  center=true);
//      translate([-RG_PCB[0]/2,RG_PCB[1]/2,-corr])   cylinder(h=LED_screw_h, d=2.8,  center=true);  
//        } 
//    }
}
  
  echo("int_top_cyl_r is",int_top_cyl_r);
// translate([ 0.00, 0.00, 50 ]) top_part_cone();    

module top_part_cone(){
      difference(){
                 translate([ 0.00, 0.00, focus_h/2 ]) color("blue")  cylinder( r=int_top_cyl_r+wall*2, h=focus_h, center=true);      
            translate([ 0.00, 0.00,focus_h/2 ]) color("white") cylinder( r=int_top_cyl_r, h=focus_h+corr, center=true);
          echo("int_top_cyl_r is",int_top_cyl_r);
//wire clearance
                  translate([int_top_cyl_r-wall,0, focus_h]) color("red")    cube([wire_clearance_w,wire_clearance_w,h_ring/4],center = true);
}
//cable riel
               translate([int_top_cyl_r+wall+wire_clearance_x/2-wall,0, focus_h-wire_riel_h/2])  difference(){
                 color("red")    cube([wire_clearance_x,wire_clearance_w+wall*4,wire_riel_h],center = true);
 color("white")    cube([wire_clearance_x,wire_clearance_w,focus_h+corr],center = true);

//wire clearance
                 translate([-wire_clearance_w/2-wall,0, focus_h/3]) color("green")    cube([wire_clearance_w,wire_clearance_w,h_ring/4],center = true);
                  }
  
        } 
    
    
//  translate([ 0,0,h_cam+ h_ring+20])   RG_ring();
 module RG_ring(){
  difference(){
      circle(RG_ring_r);
     circle(40/2);
 }}   
 
module joint_top(){ difference(){
                       color("purple")    cube([sq_x+wall*10,sq_y+wall*10,h_ring],center = true);
          translate([ 0.00, 0.00, 0 ])         color("yellow")    cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,h_ring+corr*2],center = true);
            
            }}
            
module joint_bottom(){
       difference(){
        color("green")    cube([sq_x+wall*6,sq_y+wall*6,h_ring],center = true);
//       color("white") cylinder( r=cone_r+wall-corr*2, h=h_ring*0.75);
       translate([ 0, 0, -corr/2]) color("teal") cube([sq_x+corr,sq_y+corr,h_ring+corr*2],center = true);    
           
           echo("tamaño cuadrado de acrilico", sq_x+corr);
      }}
            
 h_cam_short=5;
//cone_hull_short();
module cone_hull_short(){
      translate([ 0,0,h_ring])    translate([ 0.00, 0.00, h_cam_short-corr])  top_part_cone(); 
                    
 //hull part
       difference(){
            union(){
                hull(){
               translate([ 0.00, 0.00, h_ring ]) color("white") cylinder(r=int_top_cyl_r+wall*2, h=h_cam_short);
                      color("white")  cube([sq_x+wall*10,sq_y+wall*10,1],center = true);
                }
                   hull(){
               translate([ 0.00, 0.00, h_ring ]) color("yellow") cylinder(r=int_top_cyl_r+wall*2, h=h_cam_short);
                  translate([sq_x/2+wall*4, -raspi_board[1]/2, -h_ring ])  rotate([90,0,90])  cube([raspi_board[0]-20,raspi_board[1],2]); 
                }}
                      
                   hull(){
                    translate([ 0.00, 0.00, h_ring+corr ])  cylinder( r=int_top_cyl_r, h=h_cam_short);
                    translate([ 0.00, 0.00, -corr ])    color("white") cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,1],center = true);
}         
translate([ 0.00, 0.00, -h_ring/2 ])         color("yellow")    cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,h_ring+corr*2],center = true);
            }
          //joint    
         translate([ 0.00, 0.00, -h_ring/2 ])  difference(){
             joint_top();
              //wire clearance
                  translate([ -sq_y/2-wall*2, -sq_y/2-wall*2, -h_ring/2]) color("red")    cube([wall*8,wall*3,h_ring/4],center = true);
         }
       
                          translate([sq_x/2+wall*4, -raspi_board[1]/2, -h_ring ])  rotate([90,0,90])     RPI_holder();

}
   
//---------------------------------- white light holder and cover
 


/////////////////////////
// user defined values //
/////////////////////////
dif_r_int = 48; // internal radius
ri_thick = 1; // structure internal thickness
re_thick_u = 3; // structure external thickness
re_thick_d = 1; // structure external thickness
dif_z_thick = 2; // z structure thickness
paper_space = 0.5; // space to fit the paper
h_int = 3; // internal height where to fit paper

// external square support
sq_x = 126;
sq_y = 126;
sq_thick = 2;

c_hole_w = 3;  //cable hole wide
c_hole_h = 3; //cable hole height
b_dist = 6; // base support border distance, defined on the central axis
b_thick = 2;
dif_base_h = 15.8-sq_thick+dif_z_thick;  // related to diffuser h

x_displace = 0;//3;  // hole displacement arround x axis


// computed values
r_ext_up = dif_r_int+re_thick_u+ri_thick+paper_space;
r_ext_down = dif_r_int+re_thick_d+ri_thick+paper_space;
h_total = h_int+dif_z_thick;



module ring(H,re_up,re_down,ri){
    difference(){
    cylinder(h = H, r1 = re_down, r2= re_up, center = true,$fn = 100);
        cylinder(h = H, r = ri, center = true,$fn = 100);
    }
    
}


module square_structure(){
    
    //base_x = sq_x - b_dist_x;
    //base_y = sq_y - b_dist_y;
    r_b = (sq_x-b_dist)/2;
    ri_b = r_b - b_thick;
    
    translate([0,0,-sq_thick/2])
    difference(){
        translate([x_displace,0,0])
    cube([sq_x,sq_y,sq_thick], center = true);

        translate([0,0,0])
            cylinder(h = sq_thick, r = r_ext_up, center = true,$fn = 100);translate([x_displace+(c_hole_w-sq_x)/2,(c_hole_w-sq_y)/2,0])
            cube([c_hole_w,c_hole_h,sq_thick], center = true);

    }
    

    translate([0,0,-dif_base_h/2-sq_thick])
    difference(){
    ring(dif_base_h,r_b,r_b,ri_b);
        //this part should be corrected...
        // it's not a general solution
    rotate(230)
   translate([r_b/2,0,-dif_base_h/2])
    cube([r_b/2,c_hole_w,c_hole_w]);
    }

/*
        
    translate([0,0,-dif_base_h/2-sq_thick])
    difference(){
    cube([base_x,base_y,dif_base_h], center = true);
    cube([base_x-sq_thick,base_y-sq_thick,dif_base_h], center = true);
        translate([(sq_thick-base_x)/2,c_hole_w-base_y/2,(c_hole_h-dif_base_h)/2])
            cube([sq_thick,c_hole_w,c_hole_h], center = true);
    }
    
*/
    
    
}
diffuser_holder(true);
module diffuser_holder(sq){
    
    re_space = r_ext_down-re_thick_d;
    ri_space = dif_r_int+ri_thick;
    
        translate([0,0,-h_total/2])
    difference(){
    ring(h_total,r_ext_up,r_ext_down,dif_r_int);
        translate([0,0,-dif_z_thick])ring(h_total,re_space,re_space,ri_space);
    }
    
    if (sq == true){

    square_structure();

    } 
}


//
//module ring(H,re_up,re_down,ri){
//    difference(){
//    cylinder(h = H, r1 = re_down, r2= re_up, center = true,$fn = 100);
//       translate([0,0,0]) cylinder(h = H, r = ri, center = true,$fn = 100);
//    }
//    
//}
//
//
//module square_structure(){
//   
//    r_b = (sq_x-b_dist)/2;
//    ri_b = r_b - b_thick;
//    
//    translate([0,0,-sq_thick/2])
//    difference(){
//        translate([x_displace,0,0])
//    cube([sq_x,sq_y,sq_thick], center = true);
//
//        translate([0,0,0])
//            cylinder(h = sq_thick, r = r_ext_up, center = true,$fn = 100);//translate([x_displace+(c_hole_w-sq_x)/2,(c_hole_w-sq_y)/2,0])
//           // cube([c_hole_w,c_hole_h,sq_thick], center = true);
//    }
//    translate([0,0,-base_h_sq/2-sq_thick])
//    difference(){
//    ring(base_h_sq,r_b,r_b,ri_b);
//        //this part should be corrected...
//        // it's not a general solution
//    rotate(230)
//   translate([r_b/2,0,-base_h_sq/2])
//    cube([r_b/2,c_hole_w,c_hole_w]);
//    }
//}
//
//translate([0,0,145])diffuser_holder(true);
//module diffuser_holder(sq){
//    
//    re_space = r_ext_down-re_thick_d;
//    ri_space = r_int+ri_thick;
//    
//        translate([0,0,-h_total/2])
//    difference(){
//    ring(h_total,r_ext_up,r_ext_down,r_int);
//        translate([0,0,-z_thick])ring(h_total,re_space,re_space,ri_space);
//    }
//    
//    if (sq == true){
//    square_structure();
//    }
////orejitas
//      rotate([0,0,45]) union(){ translate([0,sq_x/2-wall*8,h_total/2]) cube([sq_x/6,wall*2,h_total], center=true);
//      translate([0,-sq_x/2+wall*8,h_total/2]) cube([sq_x/6,wall*2,h_total], center=true);
//      }
//}

//---------------------------------- plate and filter holder 


//translate([0,0,90])plate_holder();
module plate_holder(){
//top part holding the plate and interfacing with lid
  translate([ 0, 0, h_ring/2]) difference(){
      joint_bottom();
        //wire clearance
        translate([ -sq_y/2, -sq_y/2, 0]) color("red")    cube([wall*8,wall*3,h_ring],center = true);
  }
//interface between top and bottom 
      difference(){
          translate([ 0, 0, wall-corr/2]) color("white") cube([sq_x+wall*6+corr*10,sq_y+wall*6+corr*10,wall*2],center = true);
       color("red") cylinder(r=  petri_lid_d/2+wall*6, h=h_ring*5, center = true);// hole for illumination
          echo("radious plate hole", petri_lid_d/2+wall*6);
      }

//ring for top part joining printed lighting cylinder 
translate([ 0, 0, -h_ring/2+wall*2])   joint_top();
}
    
wire_tunnel_h=35;
//translate([ 0, 0, 0  ]) lighting_base_squared();
module lighting_base_squared(){
     translate([0,0,-wall]) joint_bottom(); 
   translate([0,0,-h_ring]) difference(){
                       union(){
       color("purple")    cube([sq_x+wall*10,sq_y+wall*10,h_ring],center = true);
          //wire cable tunnel to avoid light pollution in
          translate([sq_x/2+wall*4,sq_x/2-wire_tunnel_h/2+wall*4,+wall*4]) difference(){
            translate([ 0, 0,-h_ring/2+ wall*6 ]) rotate([90,0,0]) cylinder(r=5+wall*3, h=wire_tunnel_h, center = true);
          translate([ 0, -wall*2,-h_ring/2+ wall*6 ]) rotate([90,0,0])cylinder(r=5, h=wire_tunnel_h, center = true);   
      }

      }
                translate([ 0.00, 0.00, wall*4 ])       color("teal") cube([sq_x+corr,sq_y+corr,h_ring+corr*2],center = true);    

       //cable hole
          translate([ sq_x/2, sq_x/2-wall*2,-h_ring/2+ wall*6 ])    cube([8,3,3],center = true);    
            }

       //support to screw in the LED PCB
        translate([ 0, 0, raspi_z/2-h_ring-h_ring/2 ])  PCB_LED_support();    
    }
    
    
//---------------------------deprecated modules



    

//translate([ 0,0,50 ]) extension_ring_long_v2();
module extension_ring_long_v2(){
//---------------- top part holding the plate and interfacing with lid 
   difference(){
       color("grey") cylinder( r=cone_r+wall, h=h_ring/2);
       translate([ 0.00, 0.00, -h_ring]) color("red") cylinder( r=cone_r-wall*2, h=h_ring*2);
      }
      //bottom part
 translate([ 0.00, 0.00, -h_ring*2]) difference(){
            color("blue")cylinder( r=cone_r+wall*3, h=h_ring*2);
            translate([ 0.00, 0.00, 0]) color("red") cylinder( r=cone_r-wall*2, h=h_ring*3);
            translate([ 0.00, 0.00, -h_ring/2]) color("green") cylinder( r=cone_r+wall+corr, h=h_ring);
            translate([ 0.00, 0.00, h_ring/2]) color("yellow") cylinder(r=cone_r-wall*5, h=h_ring, center = true); 
           } 
}





  
  
//camera_holder(2);
 module camera_holder(type){
    if(type==1){
        RPI_lens();
    }
   else  if (type==2){
    M12_push_fit();
    }
    else  if (type==3){
    M12_screwed();
        }}
   
module RPI_lens(){
    difference() {
			union() {
                translate([0,0,wall]) 
                color("Blue") cube([base_xy, base_xy, wall*8], center = true);
               				rotate([ 0.00, 0.00, 45.00 ]) camera_mount_FF();
			}	
        translate([0, 0, -base_h/2])  cylinder (r1=((M12_r*2)+(corr*5))/2, r2=((M12_r*2)+(corr*5)), h=mount_h*2);
	}
}

//-----------------  M12lens holder attached by a push-fit mechanism
module M12_push_fit(){
    difference() {
			union() {
                translate([0,0,mount_h/2]) 
                color("Blue") cube([base_xy, base_xy, mount_h], center = true);
               				rotate([ 0.00, 0.00, 45.00 ]) camera_mount_FF();
			}	
            // adjuted diameter reducing 3 to 3 corr (14 Feb 2019)
        translate([0, 0, -base_h/2])  english_thread (diameter=(((M12_r*2)+(corr*2))/25.4), threads_per_inch=50.8, length=mount_h*1.5/25.4,internal=true, n_starts=1, thread_size=-1, groove=true,square=false, rectangle=0, angle=30, taper=0, leadin=1);
	}
}

//----------------- M12lens  holder attached with screws
/*
RPI camera dimensions: https://www.raspberrypi-spy.co.uk/2013/05/pi-camera-module-mechanical-dimensions/

25x24x9

--------25 mm (x)----
______________
|o    21mm        o|
|12.5                     |
|o                        o|   24 (y)
|9.5                       |
|_____________|
*/

//distance btwn top and mid holes
d_top_mid_holes=12.5;

//distance bwn mid holes and bottom
d_mid_holes=9.5;
cam_x=25;
cam_y=24;



//M12_screwed();
module M12_screwed(){
    difference() {
			union() {  
               translate([0,0,M12_h/2 + base_h]) 
                color("Blue") cube([base_xy/*+corr*/, base_xy/*+corr*/, M12_h], center = true);//one corr (M12_holder_concorr) vs no corr (M12_holder_sin)  to fit well (cone already has corr*2)
				translate([0,0-(cam_y/2-d_mid_holes),base_h/2])
					color("Red")  cube([cam_x, cam_y, base_h], center = true);
//				translate([screw_d/2, 0, 0])
//					color("cyan") cylinder(r = screw_hold_r, h = base_h/2);
//				translate(-[screw_d/2, 0, 0])
//					color("purple") cylinder(r = screw_hold_r, h = base_h/2);
//					translate([0,0,base_h/2/2])
//						color("white") cube([screw_d, 4, base_h/2], center = true);
			}
		translate([0,-(cam_y/2-d_mid_holes),base_h/2-wall])
			color("Green") cube([cam_x - wall*10, cam_y - wall*2, base_h+corr], center = true);
            
            //mid holes
		translate([screw_d/2, 0, 0])
			cylinder(r = screw_r, h = base_h);
		translate([-screw_d/2, 0, 0])
			cylinder(r = screw_r, h = base_h);
            
            //top holes
            translate([screw_d/2, -d_top_mid_holes, 0])
			cylinder(r = screw_r, h = base_h);
		translate([-screw_d/2,  -d_top_mid_holes, 0])
			cylinder(r = screw_r, h = base_h);
            
		translate([0, base_xy / 4, sensor_h/2])
			cube([sensor_x, base_xy / 2, sensor_h], center = true);
        translate([0, 0, base_h-wall])     cube([sensor_x, base_xy / 2, sensor_h], center = true);
//            english_thread (diameter=(((M12_r*2)+(corr*2))/25.4), threads_per_inch=50.8, length=M12_h*1.1/25.4,internal=true, n_starts=1, thread_size=-1, groove=true,square=false, rectangle=0, angle=30, taper=0, leadin=1);
	}
}


//LED_base();
module LED_base(){
     difference(){
         rotate_extrude($fn=200) polygon( points=[[LED_ring_ext_d/2,0],[LED_ring_int_d/2,0],[LED_ring_ext_d/2,LED_base_h]] );
        translate([LED_ring_int_d/2-wall*2,0,wall*6]) rotate([90,90,90])  color("blue") cube([ 15,10,15 ]);
     }
}

//------------------straight
module velvet_background_ring_v3(){
    difference(){
        cylinder( r=velvet_background_ring_d/2, h=velvet_background_ring_h);
        translate([ 0.00, 0.00, wall*2 ]) cylinder( r=velvet_background_ring_d/2-wall, h=velvet_background_ring_h); 
        }}
//---------------------inward     
module velvet_background_ring_v2(){
    difference(){
        rotate_extrude($fn=200) polygon( points=[[0,0],[velvet_background_ring_d/2,0],[velvet_background_ring_stage_r,velvet_background_ring_h],[0,velvet_background_ring_h]] );
      translate([ 0.00, 0.00, wall*2 ]) cylinder(r1= velvet_background_ring_stage_r+wall*4, r2=velvet_background_ring_stage_r, h=velvet_background_ring_h+wall); 
        }
}
//----------------------outward
module velvet_background_ring_v1(){
    difference(){
        rotate_extrude($fn=200) polygon( points=[[0,0],[velvet_background_ring_d/2,0],[velvet_background_ring_stage_r,velvet_background_ring_h],[0,velvet_background_ring_h]] );
          rotate_extrude($fn=200) polygon( points=[[0,0],[velvet_background_ring_d/2-wall*2,0],[velvet_background_ring_stage_r-wall*2,velvet_background_ring_h-wall*2],[0,velvet_background_ring_h-wall*2]] ); 
        }
}

/*--------------------------------------------------------------------------------------------------------
These modules below use Richard Bowman's code to make push fit camera holder and cover. See openflexure for mor einformation (https://github.com/rwb27/openflexure_microscope). Module camera_mount_FF and RPIcam_cover were modified from Richard ´s code
--------------------------------------------------------------------------------------------------------*/

module camera_mount_FF(){
    // A mount for the pi camera v2
    // This should finish at z=0+d, with a surface that can be
    // hull-ed onto the lens assembly.
    h = 24;
    w = 25;
    rotate(45) difference(){
        translate([0,2.4,0]) sequential_hull(){
            translate([0,0,bottom]) cube([w,h,d],center=true);
            translate([0,0,bottom+1.5]) cube([w,h,d],center=true);
            translate([0,0,0]) cube([w-(-1.5-bottom)*2,h,d],center=true);
        }
        translate([0,0,bottom]) picam2_push_fit_FF();
    }
}

module RPIcam_cover(){
    fit_corr=1;//makes it bigger to fit and avoid damaging the PCB
    // A cover for the camera PCB, slips over the bottom of the camera
    // mount.  This version should be compatible with v1 and v2 of the board
    start_y=-12+2.4;//-3.25;
    l=-start_y+12+2.4; //we start just after the socket and finish at 
    //the end of the board - this is that distance!
    difference(){
        union(){
            //base
            translate([-15,start_y,-4.3]) cube([25+5,l,4.3+d]);
            //grippers
            reflect([1,0,0]) translate([-15,start_y,fit_corr]){
                translate([0,0,-fit_corr]) cube([2,l,4.5-d]);
                hull(){
                    translate([0,0,1.5]) cube([2,l,3]);
                    translate([0,0,4]) cube([2+2.5,l,0.5]);
                }
            }
        }
        translate([0,0,-1]) picam2_pcb_bottom();
        //chamfer the connector edge for ease of access
        translate([-999,start_y,0]) rotate([-135,0,0]) cube([9999,999,999]);
    }
} 


 module picam2_push_fit_FF( beam_length=15){
    // This module is designed to be subtracted from the bottom of a shape.
    // The z=0 plane should be the print bed.
    // It includes cut-outs for the components on the PCB and also a push-fit hole
    // for the camera module.  This uses flexible "fingers" to grip the camera firmly
    // but gently.  Just push to insert, and wiggle to remove.  You may find popping 
    // off the brown ribbon cable and removing the PCB first helps when extracting
    // the camera module again.
    camera = [8.5,8.5,2.8]; //size of camera box (NB it's now propped up on foam)
	cw = camera[0]+1; //side length of camera box at bottom (slightly larger)
	finger_w = 1.5; //width of flexure "fingers"
	flex_l = 1; //width of flexible part
    hole_r = camera[0]/2-0.4;
	union(){
       
		//cut-out for camera
        /*hull(){
            translate([0,0,-d]) cube([cw+0.5,cw+0.5,d],center=true); //hole for camera
            translate([0,0,1]) cube([cw-0.5,cw-0.5,d],center=true); //hole for camera
        }
        */
        rotate(180/16) cylinder(r=hole_r,h=beam_length,center=true,$fn=100); //hole for light
        
        //looser cut-out for camera, with gripping "fingers" on 3 sides
        difference(){
            //cut-out big enough to include gripping fingers
           /* intersection(){
                hull(){
                    translate([0,-(finger_w+flex_l)/2,0.5+d])
                        cube([cw+2*finger_w+2*flex_l, cw+finger_w+flex_l, 2*d],center=true);
                    translate([0,0,0.5+3*(finger_w+flex_l)]) cube([cw, cw, d],center=true);
                }
                //fill in the corners of the void first, to give an endstop for the camera
                
                //build up the roof gradually so we get a nice hole
                rotate(90) translate([0,0,camera[2]+1.0]) 
                    hole_from_bottom(r=hole_r,h=beam_length - camera[2]-1.5);
            }
            */
                
            //gripping "fingers" (NB we subtract these from the cut-out)
           /* for(a=[90:90:270]) rotate(a) hull(){
                translate([-cw/2+0.5,cw/2,0]) cube([cw-1,finger_w,d]);
                translate([-cw/2+1,camera[0]/2-0.1,camera[2]]) cube([cw-2,finger_w,d]);
            }
            */
            //there's no finger on the top, so add a dimple on the fourth side
            /*hull(){
                translate([-cw/2+1,cw/2,4.3/2]) cube([cw-2,d,camera[2]-1.5]);
                translate([-cw/2+2,camera[1]/2,camera[2]-0.5]) cube([cw-4,d,0.5]);
                translate([-21/2,cw/2,camera[2]-1.5]) cube([21,d,camera[2]-1.5]);
                translate([-21/2,camera[1]/2,camera[2]-0.5]) cube([21,d,0.5]);
            }
            */
		}
        
		//ribbon cable at top of camera
        sequential_hull(){
            translate([0,-5,0]) cube([cw-1,d,5],center=true);
            translate([0,cw/2+1,0]) cube([cw-1,d,5],center=true);
            translate([0,9.4-(4.4/1)/2,0]) cube([cw-1,1,5],center=true);
        }
        //flex connector
        translate([-1.25,9.4,0]) cube([cw-1+2.5, 4.4+1, 5],center=true);
        
		//screw holes for safety (M2 "threaded")
		reflect([1,0,0]) translate([21/2,0,0]){
            cylinder(r1=2.5, r2=1, h=2, center=true, $fn=100);
            cylinder(r=1, h=7, $fn=100);
        }
	}
}



module Cylindrical_lid(){
   union(){
       translate([ 0,0,h_ring]) difference(){
       cylinder( r=petri_lid_d/2+wall*2, h=h_cam);
       translate([ 0.00, 0.00, -wall ]) color("red") cylinder( r=petri_lid_d/2, h=h_cam);
       translate([ 0.00, 0.00, h_cam ])color("red") cube([base_xy+corr, base_xy+corr, wall*2+corr], center = true);}
       difference(){
       cylinder( r=petri_lid_d/2+wall*3, h=h_ring);
       translate([ 0.00, 0.00, h_ring/2]) color("blue") cylinder( r=petri_lid_d/2, h=h_ring);
       translate([ 0.00, 0.00, -h_ring/2-wall]) color("green") cylinder( r=petri_lid_d/2+wall+corr, h=h_ring);
       color("red") cylinder(r=petri_lid_d/2-wall*5, h=h_ring*3, center = true); 
           }    
}}

module plate_ring(type){
     if(type==1){
//to do
         }
    else if(type==2){
        ring_v2();
}
    else if(type==3){
        ring_v3();
}
    }
    
//-----------------------big ring
module ring_v3(){
  difference(){// top part holding the plate and interfacing with lid
       translate([ 0.00, 0.00, h_ring/2])  cylinder( r=petri_lid_d/2+wall, h=h_ring/2);
       translate([ 0.00, 0.00, h_ring/2]) color("cyan") cylinder( r=petri_lid_d/2-wall, h=h_ring*1.5);
       color("cyan") cylinder(r=elastic_holder_dist/2, h=h_ring*3, center = true);   
      }
      difference(){//bottom part sitting on top of base
       cylinder( r=base_d/2+wall*3, h=h_ring/2);
     
       translate([ 0.00, 0.00, -h_ring/2-wall*3]) color("blue") cylinder( r=base_d/2, h=h_ring);
       color("cyan") cylinder(r=elastic_holder_dist/2, h=h_ring*3, center = true);// hole for illumination
}}
 
//---------------------ring to be inserted in cardboard box hole
module ring_v2(){
  difference(){
      union(){
          translate([ 0.00, 0.00, h_ring/2])  cylinder( r=petri_lid_d/2+wall, h=h_ring/2);
          translate([ 0.00, 0.00, h_ring/2])  cube([ petri_lid_d*1.5, petri_lid_d*1.5, wall*2 ], center=true);
          }
       translate([ 0.00, 0.00, h_ring/2]) color("red") cylinder( r=petri_lid_d/2-wall, h=h_ring*1.5);
       color("cyan") cylinder(r=elastic_holder_dist/2, h=h_ring*3, center = true);   
      }
      difference(){
       cylinder( r=petri_lid_d/2+wall*2, h=h_ring/2);
      
       translate([ 0.00, 0.00, -h_ring/2-wall]) color("blue") cylinder( r=petri_lid_d/2, h=h_ring);
       color("cyan") cylinder(r=elastic_holder_dist/2, h=h_ring*3, center = true);   
}}



//top_part_cone_old();                 
module top_part_cone_old(){

    difference(){
       union(){
           translate([ 0.00, 0.00, focus_h-mount_h/2+wall*3 ])    cube([base_xy+wall*3, base_xy+wall*3, mount_h], center = true);
      difference(){
            union(){
                 translate([ 0.00, 0.00, focus_h/2 ]) color("green")  cylinder( r=cone_r3, h=focus_h, center=true);
            }
            translate([ 0.00, 0.00,focus_h/2-wall*2 ]) color("yellow")  cylinder( r=cone_r3-wall*3, h=focus_h-wall*2, center=true);
      translate([ 0.00, 0.00, focus_h+mount_h/2-corr ])     
    color("Blue") cube([base_xy+corr*2, base_xy+corr*2, mount_h*20], center = true);
            //operation window
          translate([ 0.00, 0.00, focus_h/2+wall*3]) minkowski(){ 
                    sphere(r=1.5); cube([ focus_r*3, focus_r, focus_h/2 ], center=true); }

}}
color("green") cube([base_xy+corr*2, base_xy+corr*2, mount_h*300], center = true);
    }
    RG_PCB=[23,60]; //M3 screw positions

  translate([ 0,0, focus_h-mount_h/2+raspi_z/2]) 
    translate([0,0,0]) difference(){
        union(){
     translate([-RG_PCB[0]/2,-RG_PCB[1]/2,0])  cylinder(h=raspi_z, d=7, center=true);
      translate([RG_PCB[0]/2,-RG_PCB[1]/2,0])  cylinder(h=raspi_z, d=7,  center=true);
      translate([RG_PCB[0]/2,RG_PCB[1]/2,0])  cylinder(h=raspi_z, d=7,  center=true);
      translate([-RG_PCB[0]/2,RG_PCB[1]/2,0])   cylinder(h=raspi_z, d=7,  center=true);  
        } 
          union(){
     translate([-RG_PCB[0]/2,-RG_PCB[1]/2,-corr])  cylinder(h=raspi_z, d=2.8, center=true);
      translate([RG_PCB[0]/2,-RG_PCB[1]/2,-corr])  cylinder(h=raspi_z, d=2.8,  center=true);
      translate([RG_PCB[0]/2,RG_PCB[1]/2,-corr])  cylinder(h=raspi_z, d=2.8,  center=true);
      translate([-RG_PCB[0]/2,RG_PCB[1]/2,-corr])   cylinder(h=raspi_z, d=2.8,  center=true);  
        } 
    }
}
  

// cone();
module cone(){
       translate([ 0,0,h_ring]) difference(){
            union(){
               color("teal") hull(){  
                    cylinder( r1=cone_r-wall*3, r2=cone_r3, h=h_cam);
                   translate([ 35.00, -raspi_board[1]/2, h_cam ])  rotate([0,70,0])      cube([raspi_board[0]-20,raspi_board[1],2]);  
                }
                //RPI part
                translate([ 0.00, 0.00, h_cam-corr])  top_part_cone(); 
              translate([ 35.00, -raspi_board[1]/2, h_cam ])  rotate([0,69,0])     RPI_holder();
                }
                 
                 //internal cone for difference
           translate([ 0.00, 0.00, -corr*6 ]) color("red") cylinder( r1=cone_r-wall*3, r2=cone_r3-wall*4, h=h_cam+corr*12);          
                }          
           //internal
       difference(){
            hull(){
               translate([ 0.00, 0.00, h_ring ]) color("blue")cylinder( r=cone_r-wall*3, h=0.1);
                      color("white")  cube([sq_x+wall*11,sq_y+wall*11,1],center = true);}
                   hull(){
                    translate([ 0.00, 0.00, h_ring+corr ])  color("purple") cylinder( r=cone_r-wall*5+corr, h=0.1);
                    translate([ 0.00, 0.00, -corr ])    color("white") cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,1],center = true);
}         
            }
          //joint    
         translate([ 0.00, 0.00, -h_ring/2 ])    difference(){
                       color("white")    cube([sq_x+wall*11,sq_y+wall*11,h_ring],center = true);
          
          translate([ 0.00, 0.00, 0 ])         color("yellow")    cube([sq_x+wall*6+corr*3,sq_y+wall*6+corr*3,h_ring+corr*2],center = true);
             //wire clearance
                  translate([ sq_y/2+wall*2, sq_y/2+wall*2, -h_ring/2]) color("red")    cube([wall*8,wall*3,h_ring/4],center = true);
            }}

//lid();
module lid(){
//top part holding the plate and interfacing with lid
  translate([ 0, 0, h_ring/2])  difference(){
        color("white")    cube([sq_x+wall*6,sq_y+wall*6,h_ring],center = true);
//       color("white") cylinder( r=cone_r+wall-corr*2, h=h_ring*0.75);
       translate([ 0, 0, -corr/2]) color("teal") cube([sq_x+corr,sq_y+corr,h_ring+corr],center = true);
//         translate([ 0, 0, -wall]) color("cyan") cylinder( r=cone_r-wall*3, h=h_ring+wall*2);
//        translate([0,0,0]) ITO();
         //wire clearance
        translate([ -sq_y/2, -sq_y/2, 0]) color("red")    cube([wall*8,wall*3,h_ring],center = true);
      }
//interface between top and bottom 
      difference(){
       translate([ 0, 0, wall]) color("black")cylinder(r=base_d/2, h=wall*2, center=true);
       color("red") cylinder(r=  r_ext_up+wall*2, h=h_ring*5, center = true);// hole for illumination
      }

//ring for top part joining  printed lighting cylinder 

    difference(){
       translate([ 0, 0, -inner_h/2])  cylinder(r=base_d/2+wall*3, h=inner_h, center=true);;
       translate([ 0, 0, -inner_h/2-wall*2]) color("orange") cylinder(r=base_d/2, h=inner_h, center=true);
    color("red") cylinder(r=  r_ext_up+wall*2, h=h_ring*5, center = true); 
    }
//holders for elastics
//difference(){
//   union(){
//       translate([0,elastic_holder_dist/2+11/2,5])  cube([elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([0,-(elastic_holder_dist/2+11/2),5])  cube([elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([elastic_holder_dist/2+11/2,0,5])  cube([ elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([-(elastic_holder_dist/2+11/2),0,5])   cube([ elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  };
// union(){
//       translate([0,elastic_holder_dist/2+11/2+elastic_holder_xy/2,0])  cube([elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([0,-(elastic_holder_dist/2+11/2+elastic_holder_xy/2),0])  cube([elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([elastic_holder_dist/2+11/2+elastic_holder_xy/2,0,0])  cube([ elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true);  
// translate([-(elastic_holder_dist/2+11/2+elastic_holder_xy/2),0,0])   cube([ elastic_holder_xy,elastic_holder_xy,elastic_holder_z], center=true); 
//      translate([0,0,0]) ITO();
//     }

//uncoment to see petri lid size
//%cylinder(r=(petri_lid_d)/2,h=40);

}

module ventilation(){
    vent_x=120;
    vent_y=70;
    cube_d=4;
    space=15;
    for ( i=[0:space:vent_x]) {
for ( j=[0:space:vent_y]) {
    translate([-vent_x/2-space/2+cube_d+i,-vent_y/2+space/2-cube_d+j,-cube_d/2])
    cube([cube_d, cube_d, 10],center=true);
}}
}

            

//          
////cone_hull();
//module cone_hull(){
//       translate([ 0,0,h_ring]) difference(){
//            union(){
//               color("teal") hull(){  
//                   color("white") cylinder( r1=cone_r-wall*3, r2=cone_r3, h=h_cam);
//                   translate([ 35.00, -raspi_board[1]/2, h_cam ])  rotate([0,70,0])      cube([raspi_board[0]-20,raspi_board[1],2]);  
//                }
//                //RPI part
//                translate([ 0.00, 0.00, h_cam-corr])  top_part_cone(); 
//              translate([ 35.00, -raspi_board[1]/2, h_cam ])  rotate([0,69,0])     RPI_holder();
//                }
//                 
//                 //internal cone for difference
//           translate([ 0.00, 0.00, -corr*6 ]) color("red") cylinder( r1=cone_r-wall*3, r2=cone_r3-wall*4, h=h_cam+corr*12);          
//                }          
// //internal
//       difference(){
//            hull(){
//               translate([ 0.00, 0.00, h_ring ]) color("blue")cylinder( r=cone_r-wall*3, h=0.1);
//                      color("white")  cube([sq_x+wall*10,sq_y+wall*10,1],center = true);}
//                   hull(){
//                    translate([ 0.00, 0.00, h_ring+corr ])  color("purple") cylinder( r=cone_r-wall*5+corr, h=0.1);
//                    translate([ 0.00, 0.00, -corr ])    color("white") cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,1],center = true);
//}         
//            }
//          //joint    
//         translate([ 0.00, 0.00, -h_ring/2 ])    difference(){
//                       color("white")    cube([sq_x+wall*10,sq_y+wall*10,h_ring],center = true);
//          translate([ 0.00, 0.00, 0 ])         color("white")    cube([sq_x+wall*6+corr*2,sq_y+wall*6+corr*2,h_ring+corr*2],center = true);
//             //wire clearance
//                  translate([ -sq_y/2-wall*2, -sq_y/2-wall*2, -h_ring/2]) color("red")    cube([wall*8,wall*3,h_ring/4],center = true);
//            }}
//               
//
//
////    //cone();
////module cone(){
//       translate([ 0,0,h_ring]) difference(){
//            union(){
//                hull(){ color("lightgreen") cylinder( r1=cone_r+wall*3, r2=cone_r2, h=h_cam);
//                   translate([ 30.00, -raspi_board[1]/2, h_cam ])  rotate([0,50,0])      cube([raspi_board[0]-20,raspi_board[1],2]);  
//                }
//                //top_part
//                translate([ 0.00, 0.00, h_cam-corr])  top_part_cone(); 
//              translate([ 30.00, -raspi_board[1]/2, h_cam ])  rotate([0,50,0])     RPI_holder();
//                }               
//                 //internal cone for difference
//            translate([ 0.00, 0.00, -corr ]) color("red") cylinder( r1=cone_r+wall, r2=cone_r2-wall*2, h=h_cam+corr*9);                  
//                }             
//       difference(){//ring base
//            color("blue")cylinder( r=cone_r+wall*3, h=h_ring);
//            translate([ 0.00, 0.00, h_ring/1.5-corr]) color("green") cylinder( r1=cone_r-wall*2, r2=cone_r+wall,h=h_ring+corr);
//            translate([ 0.00, 0.00, -h_ring/3]) color("purple") cylinder( r=cone_r+wall+corr, h=h_ring);
//           }    }

// translate([ 0, 0, 2  ]) lighting_base();
module lighting_base(){
    difference(){
       color("violet")cylinder(r=base_d/2-corr*2, h=light_box_h);
       translate([ 0, 0,  wall*3 ]) color("red") cylinder( r=base_d/2-wall*4, h=light_box_h);
      translate([base_d/2-wall*5,0,wall*11]) rotate([90,90,90])  color("blue") cylinder(r=wall*8, h=wall*10);
        //ventilation holes
//        ventilation(); //be careful, light might come in and heat from LEDs is not a real problem, therefore ventilation has been eliminated
        
           }
       //support to screw in the LED PCB
        translate([ 0, 0, raspi_z/2  ])  PCB_LED_support();    
    }
