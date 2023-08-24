from st3m.application import Application, ApplicationContext
from st3m.ui.colours import PUSH_RED, GO_GREEN, BLACK
from st3m.goose import Dict, Any, Tuple
from st3m.input import InputState
from ctx import Context
import captouch
import leds
import json
import math
import random
import time


class Configuration:
    def __init__(self) -> None:
        self.ledMode = 0

    @classmethod
    def load(cls, path: str) -> "Configuration":
        res = cls()
        try:
            with open(path) as f:
                jsondata = f.read()
            data = json.loads(jsondata)
        except OSError:
            data = {
                "swapMode": 1,
                "swapCD": 1,
                "text_swapCD": 3,
                "selectedText": 0,
                "mode": 3,
                "glichMode": 3,
                "font": 1,
                "text1": [
                    ["Text1?", 60, 25, "0x1EE210", "0xFFE599"],
                    ["Text2", 60, 25, "0x1EE210", "0xFFE599"],
                    [
                        "Text3",
                        40,
                        20,
                        "0x1EE210",
                        "0xFFE599",
                        ["/flash/sys/apps/single/heart.png", -25, 35, 50, 50],
                    ],
                ],
                "text2": [
                    ["Placeholder1", 40, 25, "0x1EE210", "0xFFE599"],
                    ["Placeholder2", 40, 25, "0x1EE210", "0xFFE599"],
                ],
                "text3": [
                    ["Placeholder3", 40, 25, "0x1EE210", "0xFFE599"],
                    ["Placeholder4", 40, 25, "0x1EE210", "0xFFE599"],
                ],
                "text4": [
                    ["Yo-Ho-Ho", 30, 25, "0x349BEB", "0x8FEB34"],
                    ["and a buddle of rum!", 25, 15, "0x349BEB", "0x8FEB34"],
                ],
                "mode": 2,
                "size": 30,
            }
            pass
        res._text = [[] for _ in range(5)]
        if "font" in data and type(data["font"]) == int:
            print("font found")
            res.font = data["font"]
        if "selectedText" in data and type(data["selectedText"]) == int:
            res.selectedText = data["selectedText"]
        if "swapMode" in data and type(data["selectedText"]) == int:
            res.swapMode = data["swapMode"]
        if "swapCD" in data and type(data["swapCD"]) == int:
            res.swapCD = data["swapCD"]
        if "text_swapCD" in data and type(data["text_swapCD"]) == int:
            res.text_swapCD = data["text_swapCD"]
        if "text1" in data and type(data["text1"]) == list:
            res._text[0] = data["text1"]
        if "text2" in data and type(data["text2"]) == list:
            res._text[1] = data["text2"]
        if "text3" in data and type(data["text3"]) == list:
            res._text[2] = data["text3"]
        if "text4" in data and type(data["text4"]) == list:
            res._text[3] = data["text4"]
        if "glichMode" in data:
            if type(data["glichMode"]) == int:
                res.glitch = int(data["glichMode"])
        if "mode" in data:
            if type(data["mode"]) == int:
                res.mode = int(data["mode"])
        return res

    def save(self, context, path: str) -> None:
        d = {
            "font": context._font,
            "text1": context._text[0],
            "text2": context._text[1],
            "text3": context._text[2],
            "text4": context._text[3],
            "swapMode": self.swapMode,
            "swapCD": self.swapCD,
            "text_swapCD": self.text_swapCD,
            "glichMode": context.glitch,
            "mode": context._config.mode,
            "selectedText": context._curTextIndex,
        }
        jsondata = json.dumps(d)
        with open(path, "w") as f:
            f.write(jsondata)
            f.close()

    def to_normalized_tuple(self, color) -> Tuple[float, float, float]:
        return (
            int(color[2:4], 16) / 255.0,
            int(color[4:6], 16) / 255.0,
            int(color[6:8], 16) / 255.0,
        )


class Single(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self._scale_name = 0.5
        self._scale_pronouns = 1.0
        self._led = 0.0
        self._phase = 0.0
        self._phaseMax = 1
        self._filename = "/flash/flow3r-dating.json"
        self._config = Configuration.load(self._filename)
        self._startTime = time.time()
        self._startTimeQR = time.time()
        self._curRound = 0
        self._curTextIndex = self._config.selectedText
        self._font = self._config.font
        self._text = self._config._text
        self._endTime = 0
        self._angle = 0.0
        self.glitchInterval = 0
        self.glitchScale = 40
        self.ledMode = 0
        self._hoverstate = False
        self.knwonLedModes = 1
        # glich Mode - das wackelt nen bisl.  default = 0 / 0 und Mode 1 (in der single.json)
        # rotieren hab ich raus gemacht, war nervig. Kann man wieder adden bei Line: 141/142 (einfach aus der original wieder kopieren)
        self.glitch = self._config.glitch
        self.moveGlitch = 2

    def draw(self, ctx: Context) -> None:
        if not self._hoverstate:
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            ctx.font = ctx.get_font_name(self._font)
            # das hier legt quasi ne Box über den ganzen Screen -120 , -120 (links oben) nach 240 ,240 (rechts unten) die App ist quasi ein "Overlay"
            ctx.rgb(0, 0, 0).rectangle(
                -120, -120, 240, 240
            ).fill()  # 0,0,0 - schwarzes Overlay
            # Das overlay wird gefärbt, dadurch entsteht die Text farbe.
            print(str(self._text[self._curTextIndex]))
            # bugfix: Switching Text when CurRound of old Text is greater then new Array length. Fallback to 0.
            if self._curRound >= len(self._text[self._curTextIndex]):
                self._curRound = 0
            ctx.rgb(
                *self._config.to_normalized_tuple(
                    self._text[self._curTextIndex][self._curRound][3]
                )
            )
            ctx.move_to(0, 0)
            ctx.save()
            if self._config.mode == 0:
                ctx.scale(self._scale_name, 1)
            elif self._config.mode == 1:
                ctx.rotate(self._angle)
            elif self._config.mode == 2:
                if self.glitch == 0:
                    ctx.text_baseline = ctx.MIDDLE
                    ctx.restore()
                if self.glitch == 1:
                    ctx.text_baseline = ctx.HANGING
                elif self.glitch == 2:
                    ctx.text_baseline = ctx.BOTTOM
                elif self.glitch == 3:
                    ctx.text_baseline = ctx.TOP
                if self.moveGlitch == 1:
                    ctx.text_baseline = ctx.BOTTOM
                elif self.moveGlitch == 2:
                    ctx.text_baseline = ctx.TOP
                if self.glitch > 0:
                    scaleInt = random.randint(1, 100) / 100
                    ctx.scale(scaleInt, scaleInt)
            self._endTime = time.time()
            # Wenn X Sekunden vorbei sind, adden wir +1 zu curRound, wenn CurRound höher ist als die Länge vom aktuell selektierten text, Fallback zu 0
            if self._endTime - self._startTime >= self._config.text_swapCD:
                self._curRound = self._curRound + 1
                self._startTime = time.time()
                if self._curRound >= len(self._text[self._curTextIndex]):
                    self._curRound = 0
            ctx.font_size = int(self._text[self._curTextIndex][self._curRound][1])
            ctx.text(self._text[self._curTextIndex][self._curRound][0])
            ctx.restore()
            # der Text für Header wird nach -60 (oben) gemoved.
            ctx.move_to(0, -60)
            movedIndex = self._curRound + 1
            if movedIndex >= len(self._text[self._curTextIndex]):
                movedIndex = 0
            ctx.rgb(
                *self._config.to_normalized_tuple(
                    self._text[self._curTextIndex][movedIndex][4]
                )
            )
            ctx.font_size = int(self._text[self._curTextIndex][movedIndex][2])
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            ctx.text(self._text[self._curTextIndex][movedIndex][0])
            ctx.save()

            if self._config.mode == 0:
                ctx.scale(self._scale_pronouns, 1)
            elif self._config.mode == 1:
                ctx.rotate(self._angle)
                ctx.restore()
            # show Image if one is added to 6th Index (5)
            if len(self._text[self._curTextIndex][self._curRound]) == 6:
                curArray = self._text[self._curTextIndex][self._curRound][5]
                img, x, y, width, height = (
                    curArray[0],
                    curArray[1],
                    curArray[2],
                    curArray[3],
                    curArray[4],
                )
                ctx.image(img, x, y, width, height)
            # control LEDs
            if self.ledMode == 0:
                for i in range(40):
                    leds.set_hsv(
                        i,
                        ((i * 9) + (self._phase * (360 / self._phaseMax))) % 360,
                        1,
                        1,
                    )
            elif self.ledMode == 1:
                for i in range(40):
                    if (int(i + self._phase * 10) % 2) == 0:
                        leds.set_hsv(
                            i,
                            ((i * 9) + (self._phase * (360 / self._phaseMax))) % 360,
                            1,
                            1,
                        )
                    else:
                        leds.set_hsv(i, 0, 0, 0)
            # elif self.ledMode == 2:
            # for i in range(39):

            leds.update()
            ctx.fill()
        else:
            ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()
            if self.ledMode == 0:
                for i in range(40):
                    leds.set_hsv(
                        i,
                        ((i * 9) + (self._phase * (360 / self._phaseMax))) % 360,
                        1,
                        1,
                    )
            elif self.ledMode == 1:
                for i in range(40):
                    if (int(i + self._phase * 10) % 2) == 0:
                        leds.set_hsv(
                            i,
                            ((i * 9) + (self._phase * (360 / self._phaseMax))) % 360,
                            1,
                            1,
                        )
                    else:
                        leds.set_hsv(i, 0, 0, 0)
            # elif self.ledMode == 2:
            # for i in range(39):
            leds.update()
            ctx.image("/flash/sys/apps/single/qr.png", -120, -120, 240, 240)
            ctx.fill()

    def on_exit(self) -> None:
        self._config.save(self, self._filename)

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)

        self._phase += delta_ms / 1000

        if self.moveGlitch != 0:
            self.moveGlitch = 0

        if (self._phase * 1000 % 1250) < 25:
            self.moveGlitch = 1
        if (self._phase * 1000 % 1250) > 1200:
            self.moveGlitch = 2

        if self.glitch == 1:
            self.glitch = 2
        elif self.glitch == 2:
            self.glitch = 3
        elif self.glitch == 3:
            self.glitch = 0

        if self._phase >= self._phaseMax:
            self._phase -= self._phaseMax
            self.glitchInterval += 1
            if self.glitchInterval > 3:
                self.glitch = 1
                self.glitchInterval = 0
        self._scale_name = math.sin(self._phase)
        self._scale_pronouns = math.cos(self._phase)

        iy = ins.imu.acc[0] * delta_ms / 10.0
        ix = ins.imu.acc[1] * delta_ms / 10.0
        ang = math.atan2(ix, iy)
        d_ang = self._angle + (ang + math.pi / 8 * math.sin(self._phase))
        self._angle -= d_ang / 20

        self._led += delta_ms / 45
        if self._led >= 40:
            self._led = 0
        ct = captouch.read()
        if ct.petals[0].pressed:
            self._endTimeQR = time.time()
            # Damit keine doppelten clicks passieren
            if self._endTimeQR - self._startTimeQR > 2:
                self._hoverstate = not self._hoverstate
                self._startTimeQR = time.time()
        # text Swapping
        if self._config.swapMode == 0:
            if ct.petals[2].pressed:
                self._endTimeQR = time.time()
                # Damit keine doppelten clicks passieren
                if self._endTimeQR - self._startTimeQR >= self._config.swapCD:
                    self._curTextIndex = 0
                    self._startTimeQR = time.time()
            if ct.petals[4].pressed:
                self._endTimeQR = time.time()
                # Damit keine doppelten clicks passieren
                if self._endTimeQR - self._startTimeQR >= self._config.swapCD:
                    self._curTextIndex = 1
                    self._startTimeQR = time.time()
            if ct.petals[6].pressed:
                self._endTimeQR = time.time()
                # Damit keine doppelten clicks passieren
                if self._endTimeQR - self._startTimeQR >= self._config.swapCD:
                    self._curTextIndex = 2
                    self._startTimeQR = time.time()
            if ct.petals[8].pressed:
                self._endTimeQR = time.time()
                # Damit keine doppelten clicks passieren
                if self._endTimeQR - self._startTimeQR >= self._config.swapCD:
                    self._curTextIndex = 3
                    self._startTimeQR = time.time()
            # end text swapping Touch
        elif self._config.swapMode == 1:
            if self.input.buttons.os.left.pressed:
                self._curTextIndex = self._curTextIndex - 1
                if 0 > self._curTextIndex:
                    self._curTextIndex = 3
            elif self.input.buttons.os.right.pressed:
                self._curTextIndex = self._curTextIndex + 1
                if self._curTextIndex > 3:
                    self._curTextIndex = 0
        if self.input.buttons.app.left.pressed:
            if self._phaseMax > 0.1:
                self._phaseMax -= 0.1
        elif self.input.buttons.app.right.pressed:
            if self._phaseMax < 20:
                self._phaseMax += 0.1
        elif self.input.buttons.app.middle.pressed:
            self.ledMode += 1
            if self.ledMode > self.knwonLedModes:
                self.ledMode = 0


# For running with `mpremote run`:
if __name__ == "__main__":
    import st3m.run

    st3m.run.run_view(Single(ApplicationContext()))
