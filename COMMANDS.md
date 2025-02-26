# Oppo UDP-20x Telnet Commands

This document lists all known Telnet commands for controlling Oppo UDP-20x series media players (e.g., UDP-203, UDP-205), sourced from community efforts and the `Oppo20XCommand.cs` file. Each command includes an English and Russian description, followed by the Telnet command itself. Commands are grouped into three categories: Basic Commands, Query Commands, and Advanced Commands.

---

## Basic Commands / Основные команды

PowerToggle / Переключение питания (вкл/выкл)  
`#POW\r`

PowerOn / Включение  
`#PON\r`

PowerOff / Выключение  
`#POF\r`

EjectToggle / Открыть/закрыть лоток диска  
`#EJT\r`

Dimmer / Затемнить дисплей передней панели  
`#DIM\r`

PureAudioToggle / Режим Pure Audio (без видео)  
`#PUR\r`

VolumeUp / Увеличить громкость  
`#VUP\r`

VolumeDown / Уменьшить громкость  
`#VDN\r`

MuteToggle / Включить/выключить звук  
`#MUT\r`

NumericKey1 / Цифровая клавиша 1  
`#NU1\r`

NumericKey2 / Цифровая клавиша 2  
`#NU2\r`

NumericKey3 / Цифровая клавиша 3  
`#NU3\r`

NumericKey4 / Цифровая клавиша 4  
`#NU4\r`

NumericKey5 / Цифровая клавиша 5  
`#NU5\r`

NumericKey6 / Цифровая клавиша 6  
`#NU6\r`

NumericKey7 / Цифровая клавиша 7  
`#NU7\r`

NumericKey8 / Цифровая клавиша 8  
`#NU8\r`

NumericKey9 / Цифровая клавиша 9  
`#NU9\r`

NumericKey0 / Цифровая клавиша 0  
`#NU0\r`

Clear / Очистить цифровой ввод  
`#CLR\r`

GoTo / Воспроизведение с указанного места  
`#GOT\r`

Home / Перейти в главное меню  
`#HOM\r`

PageUp / Показать предыдущую страницу  
`#PUP\r`

PageDown / Показать следующую страницу  
`#PDN\r`

InfoToggle / Показать/скрыть экранное меню  
`#OSD\r`

TopMenu / Показать верхнее меню BD или меню DVD  
`#TTL\r`

PopUpMenu / Показать всплывающее меню BD или меню DVD  
`#MNU\r`

UpArrow / Навигация: вверх  
`#NUP\r`

LeftArrow / Навигация: влево  
`#NLT\r`

RightArrow / Навигация: вправо  
`#NRT\r`

DownArrow / Навигация: вниз  
`#NDN\r`

Enter / Выбрать/подтвердить  
`#SEL\r`

Setup / Войти в меню настроек  
`#SET\r`

Return / Вернуться в предыдущее меню  
`#RET\r`

Red / Функция зависит от контента (красная кнопка)  
`#RED\r`

Green / Функция зависит от контента (зелёная кнопка)  
`#GRN\r`

Blue / Функция зависит от контента (синяя кнопка)  
`#BLU\r`

Yellow / Функция зависит от контента (жёлтая кнопка)  
`#YLW\r`

Stop / Остановить воспроизведение  
`#STP\r`

Play / Начать воспроизведение  
`#PLA\r`

Pause / Приостановить воспроизведение  
`#PAU\r`

Previous / Перейти к предыдущему треку  
`#PRE\r`

Reverse / Быстрая перемотка назад  
`#REV\r`

Forward / Быстрая перемотка вперёд  
`#FWD\r`

Next / Перейти к следующему треку  
`#NXT\r`

Audio / Сменить язык или канал аудио  
`#AUD\r`

Subtitle / Сменить язык субтитров  
`#SUB\r`

Angle / Сменить угол камеры  
`#ANG\r`

Zoom / Увеличить/уменьшить изображение и настроить соотношение сторон  
`#ZOM\r`

SecondaryAudioProgram / Включить/выключить вторую звуковую программу  
`#SAP\r`

ABReplay / Повторное воспроизведение выбранного участка  
`#ATB\r`

Repeat / Повторное воспроизведение  
`#RPT\r`

PictureInPicture / Показать/скрыть картинку в картинке  
`#PIP\r`

Resolution / Переключить разрешение вывода  
`#HDM\r`

SubtitleHold / Удерживать клавишу субтитров (активирует сдвиг субтитров)  
`#SUH\r`

Option / Показать/скрыть меню опций  
`#OPT\r`

ThreeD / Показать/скрыть меню преобразования 2D в 3D или настройки 3D  
`#M3D\r`

PictureAdjustment / Показать меню настройки изображения  
`#SEH\r`

HDR / Показать меню выбора HDR  
`#HDR\r`

InfoHold / Показать подробную информацию на экране  
`#INH\r`

ResolutionHold / Установить разрешение на Auto (по умолчанию)  
`#RLH\r`

AVSync / Показать меню настройки синхронизации A/V  
`#AVS\r`

GaplessPlay / Бесшовное воспроизведение (как в меню опций)  
`#GPA\r`

Noop / Нет операции  
`#NOP\r`

Input / Переключение источников (циклически)  
`#SRC\r`

---

## Query Commands / Команды запроса статуса

QueryVerboseMode / Запрос режима подробного вывода  
`#QVM\r`

QueryPowerStatus / Запрос статуса питания  
`#QPW\r`

QueryFirmwareVersion / Запрос версии прошивки  
`#QVR\r`

QueryVolume / Запрос уровня громкости  
`#QVL\r`

QueryHDMIResolution / Запрос разрешения HDMI  
`#QHD\r`

QueryPlaybackStatus / Запрос статуса воспроизведения  
`#QPL\r`

QueryTrackOrTitleElapsedTime / Запрос прошедшего времени трека/заголовка  
`#QTE\r`

QueryTrackOrTitleRemainingTime / Запрос оставшегося времени трека/заголовка  
`#QTR\r`

QueryChapterElapsedTime / Запрос прошедшего времени главы  
`#QCE\r`

QueryChapterRemainingTime / Запрос оставшегося времени главы  
`#QCR\r`

QueryTotalElapsedTime / Запрос общего прошедшего времени  
`#QEL\r`

QueryTotalRemainingTime / Запрос общего оставшегося времени  
`#QRE\r`

QueryDiscType / Запрос типа диска  
`#QDT\r`

QueryRepeatMode / Запрос режима повтора  
`#QRP\r`

QueryInputSource / Запрос текущего источника ввода  
`#QIS\r`

QueryCDDBNumber / Запрос номера CDDB  
`#QCD\r`

QueryTrackName / Запрос названия трека  
`#QTN\r`

QueryTrackAlbum / Запрос альбома трека  
`#QTA\r`

QueryTrackPerformer / Запрос исполнителя трека  
`#QTP\r`

---

## Advanced Commands / Расширенные команды

SetVerboseModeOff / Установить режим подробного вывода выключенным  
`#SVM 0\r`

SetVerboseModeUnsolicitedStatusUpdates / Включить автоматические обновления статуса (только основные изменения)  
`#SVM 2\r`

SetVerboseModeDetailedStatus / Включить подробные обновления статуса (обновление времени каждую секунду)  
`#SVM 3\r`

SetHDMIResolutionAuto / Установить разрешение HDMI на Auto  
`#SHD AUTO\r`

SetHDMIResolutionSource / Установить разрешение HDMI на источник  
`#SHD SRC\r`

SetHDMIResolutionUHDAuto / Установить разрешение HDMI на UHD Auto  
`#SHD UHD_AUTO\r`

SetHDMIResolutionUHDUHD24 / Установить разрешение HDMI на UHD 24  
`#SHD UHD24\r`

SetHDMIResolutionUHDUHD50 / Установить разрешение HDMI на UHD 50  
`#SHD UHD50\r`

SetHDMIResolutionUHDUHD60 / Установить разрешение HDMI на UHD 60  
`#SHD UHD60\r`

SetHDMIResolution1080PAuto / Установить разрешение HDMI на 1080P Auto  
`#SHD 1080P_AUTO\r`

SetHDMIResolution1080P24 / Установить разрешение HDMI на 1080P 24  
`#SHD 1080P24\r`

SetHDMIResolution1080P50 / Установить разрешение HDMI на 1080P 50  
`#SHD 1080P50\r`

SetHDMIResolution1080P60 / Установить разрешение HDMI на 1080P 60  
`#SHD 1080P60\r`

SetHDMIResolution1080I50 / Установить разрешение HDMI на 1080I 50  
`#SHD 1080I50\r`

SetHDMIResolution1080I60 / Установить разрешение HDMI на 1080I 60  
`#SHD 1080I60\r`

SetHDMIResolution720P50 / Установить разрешение HDMI на 720P 50  
`#SHD 720P50\r`

SetHDMIResolution720P60 / Установить разрешение HDMI на 720P 60  
`#SHD 720P60\r`

SetHDMIResolution576P / Установить разрешение HDMI на 576P  
`#SHD 576P\r`

SetHDMIResolution576I / Установить разрешение HDMI на 576I  
`#SHD 576I\r`

SetHDMIResolution480P / Установить разрешение HDMI на 480P  
`#SHD 480P\r`

SetHDMIResolution480I / Установить разрешение HDMI на 480I  
`#SHD 480I\r`

SetRepeatModeChapter / Повтор главы  
`#SRP CH\r`

SetRepeatModeTitle / Повтор заголовка или трека CD  
`#SRP TT\r`

SetRepeatModeAll / Повтор всего  
`#SRP ALL\r`

SetRepeatModeOff / Выключить повтор  
`#SRP OFF\r`

SetRepeatModeShuffle / Случайный порядок (Shuffle)  
`#SRP SHF\r`

SetRepeatModeRandom / Случайное воспроизведение (Random)  
`#SRP RND\r`

---

## Notes
- Commands prefixed with `#` are sent via Telnet (port 23) to the Oppo UDP-20x device.
- Descriptions are based on `Oppo20XCommand.cs` from https://github.com/henrikwidlund/unfoldedcircle-oppo.
- Some commands (e.g., `#SVL`, `#SHD`) require parameters, indicated as `<value>`.
- Not all commands were tested in this integration; use with caution for unverified ones.
