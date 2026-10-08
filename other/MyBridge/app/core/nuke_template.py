

nuke_file = '''
#! C:/Program Files/Nuke11.1v3/nuke-11.1.3.dll -nx
#write_info Write1 file:"D:/Desktop/test.mov" format:"3072 1287 1" chans:":rgba.red:rgba.green:rgba.blue:" framerange:"11 26" fps:"0" colorspace:"sRGB" datatype:"unknown" transfer:"unknown" views:"main" colorManagement:"Nuke"
version 11.1 v3
define_window_layout_xml {<?xml version="1.0" encoding="UTF-8"?>
<layout version="1.0">
    <window x="0" y="0" w="1904" h="1001" screen="0">
        <splitter orientation="1">
            <split size="40"/>
            <dock id="" hideTitles="1" activePageId="Toolbar.1">
                <page id="Toolbar.1"/>
            </dock>
            <split size="1241" stretch="1"/>
            <splitter orientation="2">
                <split size="559"/>
                <dock id="" activePageId="Viewer.1">
                    <page id="Viewer.1"/>
                </dock>
                <split size="394"/>
                <dock id="" activePageId="DAG.1" focus="true">
                    <page id="DAG.1"/>
                    <page id="Curve Editor.1"/>
                    <page id="DopeSheet.1"/>
                </dock>
            </splitter>
            <split size="615"/>
            <dock id="" activePageId="Properties.1">
                <page id="Properties.1"/>
                <page id="uk.co.thefoundry.backgroundrenderview.1"/>
            </dock>
        </splitter>
    </window>
</layout>
}
Root {
 inputs 0
 fps FRAMERATE
 name NUKEFILEPATH
 frame 11
 first_frame 11
 last_frame 26
 lock_range true
 format "2048 858 0 0 2048 858 1 A1"
 proxy false
 proxy_type scale
 proxy_format "1024 778 0 0 1024 778 1 1K_Super_35(full-ap)"
 colorManagement Nuke
 OCIO_config aces_0.1.1
 customOCIOConfigPath "C:/Program Files/Nuke12.2v5/plugins/OCIOConfigs/configs/aces_1.1/config.ocio"
 workingSpaceLUT linear
 monitorLut sRGB
 int8Lut sRGB
 int16Lut sRGB
 logLut Cineon
 floatLut linear
}
Read {
 inputs 0
 file FRAMES
 format "3072 1287 0 0 3072 1287 1 "
 last FRAMELAST
 origlast FRAMELAST
 origset true
 name Read1
 xpos -134
 ypos -105
}
Reformat {
 name Reformat1
 xpos -134
 ypos -8
}
Write {
 file OUTPUTPATH
 file_type mov
 colorspace sRGB
 mov64_codec appr
 mov_prores_codec_profile "ProRes 4:4:4:4 12-bit"
 mov_h264_codec_profile "High 4:2:0 8-bit"
 mov64_pixel_format {{0} "yuv420p\tYCbCr 4:2:0 8-bit"}
 mov64_quality High
 mov64_fast_start true
 mov64_write_timecode true
 mov64_gop_size 12
 mov64_b_frames 0
 mov64_bitrate 20000
 mov64_bitrate_tolerance 4000000
 mov64_quality_min 1
 mov64_quality_max 3
 checkHashOnRead false
 name Write1
 xpos -116
 ypos -20
}
'''