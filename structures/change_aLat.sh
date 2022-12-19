#!/bin/bash
program_path=$(pwd)

aLat=$1

cp Ti_hcp initial

xhi_new=$(echo | awk "{print 1.0*$aLat}")
yhi_new=$(echo | awk "{print 0.866025*$aLat}")
zhi_new=$(echo | awk "{print 1.588*$aLat}")
xy_new=$(echo | awk "{print 0.5*$aLat}")
pos_y=$(echo | awk "{print 0.577350269189626$aLat}")
pos_z=$(echo | awk "{print 0.794000000000000*$aLat}")

sed -i "" "s|1.0|$xhi_new|" initial
sed -i "" "s|0.866025|$yhi_new|" initial
sed -i "" "s|1.588|$zhi_new|" initial
sed -i "" "s|0.5|$xy_new|" initial
sed -i "" "s|0.577350269189626|$pos_y|" initial
sed -i "" "s|0.794000000000000|$pos_z|" initial
sed -i "" "s|ID|1|" initial
sed -i "" "s|,|.|" initial

