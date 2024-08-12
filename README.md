# GeminEye
Handheld device for visually impaired users powered by Google Gemini | Submission for the Gemini API competition

## About
Since the dawn of time mankind has never once stopped innovating, the invention of the wheel, the discovery of fire, writing systems, all the way to the space race, and AI.
However, we've not yet managed to make this world a better place for everyone despite the advancements we've made as a species. This project is an attempt at doing exactly this.
Harnessing the power of smart multi-modal models like Gemini to bring greater intractability to the world for visually impaired users. Giving them a chance to be independent and free
of constant care. While not state-of-the-art in terms of aesthetics and user design, we aim to positively impact at least one person's life with our little device.

*"Because true progress isn't just about how far we've come, but how far we can go together"*

## Features
1. Talk with Gemini using your voice
2. Interact with your surroundings using the multi-modal capabilities of Gemini Vision
3. Summarise news articles from Reddit and web searches.
4. Send emergency SOS texts and announce the date and time.

**<ins>Note: These features are built keeping visually impaired users in mind.</ins>**

## How do I make a clone?
You will need the following:
- A RPI 4/5b
- A DC-DC buck converter
- 2 18650 batteries
- An RPI Camera module
- USB Mic
- 3-4 tactile buttons/switches
- Earphone/Aux speaker

Connect everything (should be easy). The buttons use the GPIO pins 26, 22, and 17.
The DC-DC buck converter is connected to the batteries to give the Pi a constant 5V to power the Pi and its peripherals.
Once the connections are done, edit your `.bashrc` file to get `button_monitor.py` to run every time at login. And you should be set.

## Goals
- [x] Have the user successfully interact with everyday objects via the device.
- [x] Successfully get Gemini to guide the user on interacting with their surroundings.
- [x] Fetch summarised news and web searches.
- [x] Send SOS messages to an emergency contact during emergencies with the IP address, location, and a link to the image captured at that moment.
- [x] Fetch the current date and time.

#buildwithgemini #geminiapideveloper #geminiapicompetition

## License
Licensed under MIT License.

## Gallery
![pic1](https://raw.githubusercontent.com/divine-architect/GeminEye/main/img/IMG_20240812_195649630-removebg-preview.png)
![pic2](https://raw.githubusercontent.com/divine-architect/GeminEye/main/img/IMG_20240813_004103265_MF_PORTRAIT%20(1).png)
![youtube]()
