#include <3ds.h>
#include <string.h>
#include <stdio.h>
#include "3ds_platform.h"
#include "3ds_log.h"

static CtrInput sInput;

void CtrInput_Clear(void)
{
    memset(&sInput, 0, sizeof(sInput));
}

void CtrInput_Scan(void)
{
    static const uint32_t keys[] =
    {
        KEY_A, KEY_B, KEY_SELECT, KEY_START, KEY_DRIGHT,
        KEY_DLEFT, KEY_DUP, KEY_DDOWN, KEY_R, KEY_L, KEY_X, KEY_Y
    };
    CtrInputSample sample = {0};
    hidScanInput();
    uint32_t raw = hidKeysHeld();
    /* New 3DS: ZR and ZL step the fast-forward speed (OPTIONS has it too). */
    uint32_t down = hidKeysDown();
    if (down & KEY_ZR)
        CtrSettings_StepSpeed(1, false);
    if (down & KEY_ZL)
        CtrSettings_StepSpeed(-1, false);
    for (unsigned i = 0; i < sizeof(keys) / sizeof(keys[0]); ++i)
        if (raw & keys[i])
            sample.buttons |= 1u << i;
    circlePosition circle;
    hidCircleRead(&circle);
    sample.circleX = circle.dx;
    sample.circleY = circle.dy;
    sample.touchActive = (raw & KEY_TOUCH) != 0;
    if (sample.touchActive)
    {
        touchPosition touch;
        hidTouchRead(&touch);
        sample.touchX = touch.px;
        sample.touchY = touch.py;
    }
    if (down)
    {
        char btns[80];
        btns[0] = '\0';
        if (down & KEY_A) strcat(btns, "A ");
        if (down & KEY_B) strcat(btns, "B ");
        if (down & KEY_X) strcat(btns, "X ");
        if (down & KEY_Y) strcat(btns, "Y ");
        if (down & KEY_START) strcat(btns, "START ");
        if (down & KEY_SELECT) strcat(btns, "SELECT ");
        if (down & KEY_L) strcat(btns, "L ");
        if (down & KEY_R) strcat(btns, "R ");
        if (down & KEY_ZL) strcat(btns, "ZL ");
        if (down & KEY_ZR) strcat(btns, "ZR ");
        if (down & KEY_DUP) strcat(btns, "UP ");
        if (down & KEY_DDOWN) strcat(btns, "DOWN ");
        if (down & KEY_DLEFT) strcat(btns, "LEFT ");
        if (down & KEY_DRIGHT) strcat(btns, "RIGHT ");
        if (down & KEY_TOUCH)
        {
            char touchStr[24];
            snprintf(touchStr, sizeof(touchStr), "TOUCH(%u,%u) ", sample.touchX, sample.touchY);
            strcat(btns, touchStr);
        }
        if (btns[0] != '\0')
            CtrLog_Write(CTR_LOG_INPUT, "[BTN] %s", btns);
    }
    CtrInput_Update(&sInput, &sample);
}

const CtrInput *CtrInput_Get(void)
{
    return &sInput;
}
