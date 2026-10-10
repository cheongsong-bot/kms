#!/bin/sh
# 2x speed base edit, muted (silent audio track)
V="fps=30,scale=1920:1080,setsar=1,format=yuv420p"
F2="setpts=PTS/2"
BL="gblur=sigma=18,eq=brightness=-0.12:saturation=0.8"
P="scale=952:532,pad=960:540:4:4:color=0x8B1B3E,setsar=1,fps=30,format=yuv420p"
ffmpeg -v error -y \
 -ss 0 -t 4.0 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d648aaba-20261010_130311.mp4 -t 10.2 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d7d5c2be-20261010_130246.mp4 -t 5.2 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d648aaba-20261010_130311.mp4 -t 6.2 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/fde0e8b2-20261010_130230.mp4 \
 -ss 3.6 -t 6.4 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d7d5c2be-20261010_130246.mp4 -t 6.4 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/fde0e8b2-20261010_130230.mp4 -t 6.4 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/49b4549b-20261010_130334.mp4 -t 5.33 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d648aaba-20261010_130311.mp4 \
 -t 6.6 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/49b4549b-20261010_130334.mp4 -ss 0.5 -t 3.5 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/58c74756-20261010_130301.mp4 -ss 2.9 -t 7.3 -i /root/.claude/uploads/7b6f598f-8e08-5168-bd18-d1a7f0cda694/d7d5c2be-20261010_130246.mp4 \
 -f lavfi -t 30 -i anullsrc=r=48000:cl=stereo \
 -filter_complex "
[0:v]$V,$BL[s0];
[1:v]$F2,$V,trim=0:5.1[s1];
[2:v]$F2,$V,trim=0:2.6[s2];
[3:v]$F2,$V,trim=0:3.1[s3];
[4:v]$F2,$P,trim=0:3.2[g1];[5:v]$F2,$P,tpad=stop_mode=clone:stop_duration=1,trim=0:3.2[g2];
[6:v]$F2,$P,trim=0:3.2[g3];[7:v]setpts=PTS/1.66,$P,tpad=stop_mode=clone:stop_duration=1,trim=0:3.2[g4];
[g1][g2][g3][g4]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,setsar=1,format=yuv420p[s4];
[8:v]$F2,$V,trim=0:3.3[s5];
[9:v]$V,trim=0:3.5[s6];
[10:v]$V,$BL,trim=0:7.3[s7];
[s0][s1]xfade=transition=fade:duration=0.3:offset=3.7[x1];
[x1][s2]xfade=transition=slideleft:duration=0.3:offset=8.5[x2];
[x2][s3]xfade=transition=circleopen:duration=0.3:offset=10.8[x3];
[x3][s4]xfade=transition=zoomin:duration=0.3:offset=13.6[x4];
[x4][s5]xfade=transition=smoothleft:duration=0.3:offset=16.5[x5];
[x5][s6]xfade=transition=fadewhite:duration=0.3:offset=19.5[x6];
[x6][s7]xfade=transition=fade:duration=0.3:offset=22.7,trim=0:30,setpts=PTS-STARTPTS[vout]" \
 -map "[vout]" -map 11:a -c:v libx264 -preset veryfast -crf 16 -c:a aac -b:a 64k -shortest /tmp/claude-0/-home-user-kms/7b6f598f-8e08-5168-bd18-d1a7f0cda694/scratchpad/base.mp4
