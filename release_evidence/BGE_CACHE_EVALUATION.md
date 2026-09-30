# BGE Cache Evaluation


Total queries: 100
True Positives (Semantic Hits): 51
False Negatives (Missed Hits): 6
True Negatives (Correct Misses): 43
False Positives (Incorrect Hits): 0
Hit Rate (Recall): 89.47%
False Positive Rate: 0.00%
Avg Latency: 59.75ms



- Query: My TechCorp A15G tablet screen flashes and then goes completely blank whenever I tap to open an email in Gmail, and after it works for a short time it goes blank again.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 42.14ms

- Query: My Nexa X1 screen turns completely blank or white and no text appears when I search for a stock price or use the Quick Assist app, and it happens with other apps too.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 45.68ms

- Query: My Nexa Fold X1 screen went completely black, so I can't see or interact with the phone, and I'm unable to use Data Transfer or any other method to transfer my data.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 53.14ms

- Query: My TechCorp Nexa A14/A15 screen suddenly went completely black on its own after about a month of use. It doesn't display anything, even when I try to turn it on.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 43.59ms

- Query: My tablet screen stays completely blank when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed.
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 49.40ms

- Query: My tablet's screen stays dark and only three app icons are lit while the rest are dark and won't open, so nothing loads on the screen and I can't use the device.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 49.02ms

- Query: My new smartphone's main screen stays small and doesn't fill the whole display; I can't make it expand to full size and I've never seen this before.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 48.48ms

- Query: My Nexa Fold X1 inner screen stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover screen still works.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 50.16ms

- Query: My TechCorp Nexa Fold X1 screen flickers and goes blank whenever I open it, so I can't see anything or access the settings, which stops me from using the phone.
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 49.42ms

- Query: My Nexa Fold X1 screen is half black—one side of the display is completely dark while the other side works fine, so I can't access the device normally.
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 46.26ms

- Query: My Nexa X1 has a floating circle that constantly hovers on my screen and gives me quick shortcuts to recent apps, home, back, screen off, volume control, and more; I want to remove it.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 48.69ms

- Query: My Nexa X1 screen stays blank and doesn't show any activation message or anything else when I turn it on after the carrier deactivated the old phone.
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 48.40ms

- Query: My smartphone's screen is completely cracked, it's a total crack and I can't use the device.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 47.61ms

- Query: My Nexa X1 Ultra only shows a blue (or black) screen with tiny text when I try to turn it on, and it won't start up. I tried holding the power button but it doesn't help.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 53.48ms

- Query: My TechCorp X1 Ultra screen flashes extremely quickly (in milliseconds) whenever I plug in a charger, making the display unusable for a short period.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 49.12ms

- Query: 1. "My Nexa X1 screen goes completely blank, just a dark screen with occasional scrolling and no visible content, so I can't see anything or use Data Transfer to transfer data."
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 59.35ms

- Query: 1. "My Nexa Fold X1 screen is cracked again right where it folds." 2. "The touch doesn't work on certain parts of the screen." 3. "I can hardly see anything on the display."
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 53.38ms

- Query: My Nexa A14 screen looks distorted right after I received the phone, and I need a diagnostic test.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 47.63ms

- Query: My Nexa X1 screen inputs are delayed and the touch responsiveness is laggy, causing a noticeable delay when I try to interact with the phone.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 45.79ms

- Query: My Nexa X1 Ultra screen is completely black and won't turn on, even though the phone powers on, rings, and otherwise works; there is no physical damage.
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 44.02ms

- Query: turn on wi-fi
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 43.41ms

- Query: wireless networks
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 36.96ms

- Query: wlan
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 40.13ms

- Query: connect to internet
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 44.24ms

- Query: how to enable wifi
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 42.13ms

- Query: wifi settings
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 57.32ms

- Query: turn off wi-fi
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 36.50ms

- Query: wi-fi not working
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 30.52ms

- Query: cant connect to wi-fi
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 38.74ms

- Query: wi-fi toggle
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 43.56ms

- Query: connect headset
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 43.63ms

- Query: pair speakers
  - Expected Hit: True | Actual: False
  - Source: no_evidence | Latency: 37.33ms

- Query: bluetooth settings
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 42.91ms

- Query: turn on bluetooth
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 44.32ms

- Query: turn off bluetooth
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 42.03ms

- Query: bluetooth toggle
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 38.57ms

- Query: wireless headphones
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 40.26ms

- Query: bluetooth device
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 57.46ms

- Query: cant pair bluetooth
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 62.37ms

- Query: bluetooth menu
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 53.23ms

- Query: screen timeout
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 53.50ms

- Query: brightness
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 50.67ms

- Query: dark mode
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 46.63ms

- Query: display settings
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 45.93ms

- Query: screen brightness
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 44.26ms

- Query: adjust brightness
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 37.39ms

- Query: change screen timeout
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 40.13ms

- Query: make screen brighter
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 46.78ms

- Query: dim screen
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 40.32ms

- Query: display menu
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 43.86ms

- Query: My TechCorp A15G tablet battery overheates and then goes completely dead whenever I tap to open an email in Gmail, and after it works for a short time it goes dead again.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 49.79ms

- Query: My TechCorp A15G tablet audio echoes and then goes completely mute whenever I tap to open an email in Gmail, and after it works for a short time it goes mute again.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 50.09ms

- Query: My TechCorp A15G earbuds screen flashes and then goes completely blank whenever I tap to open an email in Gmail, and after it works for a short time it goes blank again.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 50.08ms

- Query: My Nexa X1 battery turns completely dead or white and no text appears when I search for a stock price or use the Quick Assist app, and it happens with other apps too.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 50.24ms

- Query: My Nexa X1 audio turns completely mute or white and no text appears when I search for a stock price or use the Quick Assist app, and it happens with other apps too.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 54.97ms

- Query: My Nexa X1 screen turns completely blank or white and no text appears when I search for a stock price or use the Quick Assist app, and it happens with other apps too.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 51.32ms

- Query: My Nexa Fold X1 battery went completely dead, so I can't see or interact with the phone, and I'm unable to use Data Transfer or any other method to transfer my data.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 55.22ms

- Query: My Nexa Fold X1 audio went completely silent, so I can't see or interact with the phone, and I'm unable to use Data Transfer or any other method to transfer my data.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 55.85ms

- Query: My Nexa Fold X1 screen went completely black, so I can't see or interact with the watch, and I'm unable to use Data Transfer or any other method to transfer my data.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 49.91ms

- Query: My TechCorp Nexa A14/A15 battery suddenly went completely dead on its own after about a month of use. It doesn't display anything, even when I try to turn it on.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 57.16ms

- Query: My TechCorp Nexa A14/A15 audio suddenly went completely silent on its own after about a month of use. It doesn't display anything, even when I try to turn it on.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 51.54ms

- Query: My TechCorp Nexa A14/A15 screen suddenly went completely black on its own after about a month of use. It doesn't display anything, even when I try to turn it on.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 59.55ms

- Query: My tablet battery stays completely dead when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 53.04ms

- Query: My tablet audio stays completely mute when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 phone, so the transfer can't proceed.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 53.02ms

- Query: My earbuds screen stays completely blank when I try to use Data Transfer to scan the QR code for transferring data from my Nexa X1 watch, so the transfer can't proceed.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 51.31ms

- Query: My tablet's battery stays dark and only three app icons are lit while the rest are dark and won't open, so nothing loads on the battery and I can't use the device.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 56.95ms

- Query: My tablet's audio stays dark and only three app icons are lit while the rest are dark and won't open, so nothing loads on the audio and I can't use the device.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 50.05ms

- Query: My earbuds's screen stays dark and only three app icons are lit while the rest are dark and won't open, so nothing loads on the screen and I can't use the accessory.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 53.91ms

- Query: My new smartphone's main battery stays small and doesn't fill the whole display; I can't make it expand to full size and I've never seen this before.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 53.74ms

- Query: My new smartphone's main audio stays small and doesn't fill the whole display; I can't make it expand to full size and I've never seen this before.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 54.31ms

- Query: My new smartwatch's main screen stays small and doesn't fill the whole display; I can't make it expand to full size and I've never seen this before.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 57.36ms

- Query: My Nexa Fold X1 inner battery stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover battery still works.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 51.15ms

- Query: My Nexa Fold X1 inner audio stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover audio still works.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 60.51ms

- Query: My Nexa Fold X1 inner screen stopped working by itself; it shows no image and doesn't respond to touch, while the outer cover screen still works.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 48.63ms

- Query: My TechCorp Nexa Fold X1 battery flickers and goes dead whenever I open it, so I can't see anything or access the settings, which stops me from using the phone.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 54.20ms

- Query: My TechCorp Nexa Fold X1 audio flickers and goes mute whenever I open it, so I can't see anything or access the settings, which stops me from using the phone.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 59.89ms

- Query: My TechCorp Nexa Fold X1 screen flickers and goes blank whenever I open it, so I can't see anything or access the settings, which stops me from using the watch.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 70.96ms

- Query: My Nexa Fold X1 battery is half dead—one side of the display is completely dark while the other side works fine, so I can't access the device normally.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 82.60ms

- Query: My Nexa Fold X1 audio is half silent—one side of the display is completely dark while the other side works fine, so I can't access the device normally.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 86.00ms

- Query: My Nexa Fold X1 screen is half black—one side of the display is completely dark while the other side works fine, so I can't access the accessory normally.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 83.28ms

- Query: My Nexa X1 has a floating circle that constantly hovers on my battery and gives me quick shortcuts to recent apps, home, back, battery off, volume control, and more; I want to remove it.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 86.68ms

- Query: My Nexa X1 has a floating circle that constantly hovers on my audio and gives me quick shortcuts to recent apps, home, back, audio off, volume control, and more; I want to remove it.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 82.83ms

- Query: My Nexa X1 has a floating circle that constantly hovers on my screen and gives me quick shortcuts to recent apps, home, back, screen off, volume control, and more; I want to remove it.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 82.22ms

- Query: My Nexa X1 battery stays dead and doesn't show any activation message or anything else when I turn it on after the carrier deactivated the old phone.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 81.64ms

- Query: My Nexa X1 audio stays mute and doesn't show any activation message or anything else when I turn it on after the carrier deactivated the old phone.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 79.43ms

- Query: My Nexa X1 screen stays blank and doesn't show any activation message or anything else when I turn it on after the carrier deactivated the old watch.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 85.85ms

- Query: My smartphone's battery is completely swelled, it's a total swell and I can't use the device.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 89.16ms

- Query: My smartphone's audio is completely distortioned, it's a total distortion and I can't use the device.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 75.72ms

- Query: My smartwatch's screen is completely cracked, it's a total crack and I can't use the accessory.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 120.28ms

- Query: My Nexa X1 Ultra only shows a blue (or dead) battery with tiny text when I try to turn it on, and it won't start up. I tried holding the power button but it doesn't help.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 116.07ms

- Query: My Nexa X1 Ultra only shows a blue (or silent) audio with tiny text when I try to turn it on, and it won't start up. I tried holding the power button but it doesn't help.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 101.46ms

- Query: My Nexa X1 Ultra only shows a blue (or black) screen with tiny text when I try to turn it on, and it won't start up. I tried holding the power button but it doesn't help.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 123.99ms

- Query: My TechCorp X1 Ultra battery overheates extremely quickly (in milliseconds) whenever I plug in a charger, making the display unusable for a short period.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 102.09ms

- Query: My TechCorp X1 Ultra audio echoes extremely quickly (in milliseconds) whenever I plug in a charger, making the display unusable for a short period.
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 100.50ms

- Query: My TechCorp X1 Ultra screen flashes extremely quickly (in milliseconds) whenever I plug in a charger, making the display unusable for a short period.
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 103.37ms

- Query: 1. "My Nexa X1 battery goes completely dead, just a dark battery with occasional scrolling and no visible content, so I can't see anything or use Data Transfer to transfer data."
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 121.97ms

- Query: 1. "My Nexa X1 audio goes completely mute, just a dark audio with occasional scrolling and no visible content, so I can't see anything or use Data Transfer to transfer data."
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 110.48ms

- Query: 1. "My Nexa X1 screen goes completely blank, just a dark screen with occasional scrolling and no visible content, so I can't see anything or use Data Transfer to transfer data."
  - Expected Hit: True | Actual: True
  - Source: semantic_cache | Latency: 88.68ms

- Query: 1. "My Nexa Fold X1 battery is swelled again right where it folds." 2. "The touch doesn't work on certain parts of the battery." 3. "I can hardly see anything on the display."
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 101.86ms

- Query: 1. "My Nexa Fold X1 audio is distortioned again right where it folds." 2. "The touch doesn't work on certain parts of the audio." 3. "I can hardly see anything on the display."
  - Expected Hit: False | Actual: False
  - Source: no_evidence | Latency: 104.29ms
