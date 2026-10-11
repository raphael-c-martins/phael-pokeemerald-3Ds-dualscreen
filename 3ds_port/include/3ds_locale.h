#ifndef CTR_LOCALE_H
#define CTR_LOCALE_H

/* By path: platform sources do not have the game's include directories. */
#include "../../include/constants/global.h"

/* The port's own interface (the bottom screen's labels, the extras, the data
 * pack errors) follows the game's language, or Brazilian Portuguese over the
 * English game when built with PORT_LANG=pt_br (CTR_LANG_PT_BR). The game's
 * own texts stay those of its ROM. */
#if CTR_LANG_PT_BR
#define CTR_TEXT(english, spanish, portuguese) (portuguese)
#elif GAME_LANGUAGE == LANGUAGE_SPANISH
#define CTR_TEXT(english, spanish, portuguese) (spanish)
#else
#define CTR_TEXT(english, spanish, portuguese) (english)
#endif

/* A text the Spanish interface still shows in English. */
#define CTR_TEXT_PT(english, portuguese) CTR_TEXT(english, english, portuguese)

#endif
