# flow3r-dating App for Flow3r Badge

## Functions

1. Add up to 4 different Texts
1. Modify Color of each Text individually.
1. Modify Text Size of each Text individually.
1. Rolling Text -> It shows current Text in the Center, upcoming Text in the Header and if you add a 6th Parameter (Image only), is shows an Image in Footer (example follows)
1. Show QR Code when touching top petal.

## Required Setup:

Generate your own QR Code and place it in the App Folder calling your Image : qr.png

I generated mine at: https://hovercode.com/ and scaled it down with Photoshop to 240x240

## Default config

- Mode: 2 = Gliching (pretty much same as on Nick App - Rotating)
- swapMode: 1 = Swap Text with the OS Button (left / right) \* OS Button is right shoulder button!
- swapCD: 1 = 1 sec, swap Cooldown, it is only used in swapMode: 0 (when using touch Buttons)

1. "text1" = Top right (petal)
1. "text2" = Bottom right (petal)
1. "text3" = Bottom left (petal)
1. "text4" = Top left (petal)

Config Breakdown:

- Example1 = Text
- 60 = Text Size on Center
- 25 = Text Size on Header
- 0x1EE210 = Text Color on Center
- 0xFFE99 = Text Color on Header

OPTIONAL: ["/flash/sys/apps/single/heart.png", -25, 35, 50, 50]

Adds an Icon to the Footer. (Only Images supported atm.)

`"text1": [["Example1", 60, 25, "0x1EE210", "0xFFE599"], ["Example2", 60, 25, "0x1EE210", "0xFFE599"], ["Example3", 40, 20, "0x1EE210", "0xFFE599", ["/flash/sys/apps/single/heart.png", -25, 35, 50, 50]]]`

Default Config:

`{"swapMode":1,"swapCD":1,"selectedText":0,"mode":3,"glichMode":3,"font":1,"text1":[["Text1?",60,25,"0x1EE210","0xFFE599"],["Text2",60,25,"0x1EE210","0xFFE599"],["Text3",40,20,"0x1EE210","0xFFE599",["/flash/sys/apps/single/heart.png",-25,35,50,50]]],"text2":[["Placeholder1",40,25,"0x1EE210","0xFFE599"],["Placeholder2",40,25,"0x1EE210","0xFFE599"]],"text3":[["Placeholder3",40,25,"0x1EE210","0xFFE599"],["Placeholder4",40,25,"0x1EE210","0xFFE599"]],"text4":[["Yo-Ho-Ho",30,25,"0x349BEB","0x8FEB34"],["and a buddle of rum!",25,15,"0x349BEB","0x8FEB34"]],"mode":2,"size":30}`

### Props to : Mychinos for the Fancy LED Stuff, I didn't touched.
