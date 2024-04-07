/*
    Isaac Núñez 2020 (CC BY 4.0; https://creativecommons.org/licenses/by/4.0/) 
 
    This code generate the estructure for the 
    white ligth module of the Fluopi equipment.
 
*/


/////////////////////////
// user defined values //
/////////////////////////
r_int = 48; // internal radius
ri_thick = 1; // structure internal thickness
re_thick_u = 3; // structure external thickness
re_thick_d = 1; // structure external thickness
z_thick = 2; // z structure thickness
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
base_h = 15.8-sq_thick+z_thick;  // related to diffuser h

x_displace = 3;  // hole displcement arround x axis


// computed values
r_ext_up = r_int+re_thick_u+ri_thick+paper_space;
r_ext_down = r_int+re_thick_d+ri_thick+paper_space;
h_total = h_int+z_thick;



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
    

    translate([0,0,-base_h/2-sq_thick])
    difference(){
    ring(base_h,r_b,r_b,ri_b);
        //this part should be corrected...
        // it's not a general solution
    rotate(230)
   translate([r_b/2,0,-base_h/2])
    cube([r_b/2,c_hole_w,c_hole_w]);
    }

/*
        
    translate([0,0,-base_h/2-sq_thick])
    difference(){
    cube([base_x,base_y,base_h], center = true);
    cube([base_x-sq_thick,base_y-sq_thick,base_h], center = true);
        translate([(sq_thick-base_x)/2,c_hole_w-base_y/2,(c_hole_h-base_h)/2])
            cube([sq_thick,c_hole_w,c_hole_h], center = true);
    }
    
*/
    
    
}

module diffuser_holder(sq){
    
    re_space = r_ext_down-re_thick_d;
    ri_space = r_int+ri_thick;
    
        translate([0,0,-h_total/2])
    difference(){
    ring(h_total,r_ext_up,r_ext_down,r_int);
        translate([0,0,-z_thick])ring(h_total,re_space,re_space,ri_space);
    }
    
    if (sq == true){
    square_structure();
    }
    
    
    
}


/*
module cam_holder_base() {
    
    difference(){
    cube([scafold_x,scafold_y,scafold_z], center=true);
     translate([0,0,sca_trans])cube([holder_x,scafold_y*1.1,holder_z], center=true);
     translate([0,sca_deep/2,0])cube([scafold_x - 2*sca_arms_width,scafold_y - sca_deep,scafold_z], center=true);
     translate([holder_x/2-sca_arms_space/2,sca_deep/2,scafold_z/2])cube([sca_arms_space,scafold_y - sca_deep,scafold_z], center=true);
     translate([-holder_x/2+sca_arms_space/2,sca_deep/2,scafold_z/2])cube([sca_arms_space,scafold_y - sca_deep,scafold_z], center=true);
        
        }
 
}

module ring_holder(){
    
     translate([0,0,ring_spacer_z])difference(){
  translate([(scafold_x+ring_hold_x)/2,(waveshare_cam_y-scafold_y)/2+back_thick,(scafold_z-ring_hold_z)/2])cube([ring_hold_x*1.1,ring_hold_y,ring_hold_z], center=true);
  translate([(scafold_x+ring_hold_x)/2+screw_x_space,(waveshare_cam_y-scafold_y)/2+back_thick,(scafold_z-ring_hold_z)/2])cube([ring_hold_x*1.1,screw_d,ring_hold_z], center=true);

  }
  translate([(scafold_x-sca_thick_side)/2,(waveshare_cam_y-scafold_y)/2+back_thick,scafold_z/2 +ring_spacer_z/2])cube([sca_thick_side,ring_hold_y,ring_spacer_z], center=true);    
    }
module camera_mount(camera){

    if(camera == waveshare){
            cam_x = waveshare_cam_x;
            cam_y = waveshare_cam_y;
            cam_z = waveshare_cam_z;
    
    support_z = cam_z+bottom_thick;
    support_y = hold_y + back_thick;
    translate([0,-scafold_y/2 + support_y/2,scafold_z/2+support_z/2])difference(){cube([cam_x+2*side_thick,support_y,support_z], center=true);
        translate([0,back_thick/2,-bottom_thick/2])cube([cam_x,hold_y,cam_z], center=true);
        translate([0,0,0])cube([cam_x - 2*hold_x,support_y,support_z], center=true);
    }
    }
}

side_thick = 2; //side support thickness
bottom_thick = 1; // bottom support thickness
back_thick
waveshare_cam_x=32.2;
waveshare_cam_y=1.5; //thickness
waveshare_cam_z=32.2;
hold_x = 4.8;    // space between border and cable conector
hold_y = 4.2;  // space between border and resistor
*/

diffuser_holder(true);
//square_structure();

/*
            rotate_extrude(angle = 120, convexity = 2){
    translate([10, 0, 0])
    square([b_thick,c_hole_h],center);
            }
*/
/*
true: to include the external square support, 
false: to just create the ring
*/