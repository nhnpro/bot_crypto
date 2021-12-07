# BombCrypto-Script

Most of this was written by Google Translate, so sorry for my english.

This is a bot for **BombCrypto** with GUI. **He can**: Login, Pass captcha, Go to heroes and send everyone to work every "N" minutes, Re-enter to the map every "N" minutes,
If he sees an error - relogin. All clicks to random places. Also he can send you telegram notification if something went wrong.

***

This is my first open source project on GitHub, so don't kick hard.
If you want to thank the author, you can send some pennies to **BSC wallet:**

**0x907Ef12D1F7Aef94e3D26a6634CF2F0C52e209F7**

***

## IMPORTANT
Developers against clickers and bots, I am not responsible for your losses.


***

## Installation and use
### First thing you need configure **Requierements.json** (any text redactor):


#### Items to support notifications

* **"user":** Bot name (if you have several)

* **"telegram chat id":** Id of your telegram chat, you can take it from the bot **@getmyid_bot**

* **"telegram bot token":** Id of your bot, which will send you notifications, please contact here **@BotFather**

The notifications look like this ![Уведомления](https://user-images.githubusercontent.com/94215621/144735331-9174e8b7-db82-43e5-866b-410af9617a42.png)


If you do not need them, then you can leave them empty, in any case do not delete them.

**Example**  
>     "user": ""

#### Mandatory items!
In order to change them, you need to understand the proccess of passing the captcha. The bot finds the slider and pulls it to the right, while doing 2 screenshots
and comparing them with each other. Because the place where the puzzle should stand is floating, then these 2 screenshots are different from each other. 
And when the puzzle falls into its rightful place, the coefficient of similarity of 2 screenshots is getting bigger. 
The bot constantly records the best moment where the coefficient was the most, so as soon as the puzzle reaches its place, then this will be the best moment.
But the bot won't stop there, he will pull the slider further in an attempt to find the moment even better, this is where our last 2 parameters come into play.
There are 2 ways to stop a bot.
1. Just put a time limit, if the bot has been searching for "N" seconds already, then return the slider to the place of the best moment and release the mouse button. 
2. The bot constantly compares the best moment and the current one, if the puzzle fits into rightfull place, then the best moment will take the value of the current
one - accordingly, there will be no differences between them. But if the puzzle goes further than its destination - then the differences between the best moment and the current one will be
getting bigger and bigger, and as soon as this difference becomes greater than "N", the bot should return to the best moment and release the mouse button.

### BUT
I don’t know why, but the settings with which everything works on my PC does not work on the server) Therefore, you may also have to play with the settings

* **"max time captcha": "25"** - The maximum time for captcha to pass in seconds. When the limit is reached, the bot will return to the best moment and release the mouse button. 
**This item cannot be empty**
* **"mouse up if top difference more than": "0.005"** - Maximum difference between best moment and current one, when this difference is reached, the bot will return to
the best moment and release the mouse button. **You can leave it empty and the bot will focus only on the first item**

**An example of working on my pc with settings: "max time captcha": "25", "mouse up if top difference more than": "0.005"**
![PC](https://user-images.githubusercontent.com/94215621/144736968-73c494c8-bb2c-4e7b-86c7-8dda9fe71736.gif)

**An example of working on a server with settings: "max time captcha": "25", "mouse up if top difference more than": ""**
![server](https://user-images.githubusercontent.com/94215621/144737060-c31a13dd-4b7a-4d72-aff2-e61621dd281c.gif)
***
### Folder Targets
The bot does not just clicks in certain places, but searches for targets on the screen. Due to this, you can keep the browser anywhere(**Except for the second monitor, it does not exist for the bot)**,
the main thing is that the whole game fits into the browser. For example, if he needs to go to heroes - then it will look for the button 'Heroes' every second and as soon as
he will see button - then it will be pressed. But for this he needs examples of buttons, for this there is a folder Targets.
####All my tests were carried out on 100% browser scale, I can not vouch for the bot to work on a different scale
Again, there are problems here, that I do not understand. Screenshots that were made on my PC do not work on the server, although the resolution is everywhere FullHD.
**So you may need to take your screenshots of the buttons**. Try to capture only the button itself,without unnecessary details. **IMPORTANT** - 
save a new screenshot with the same name and expansion.And also make sure that the center of the screenshot matches with the center of button, 
otherwise, due to the fact that the bot clicks every time in a random place(within a button), then he can not hit it.
***
### Folder temp
2 screenshots that are needed to complete the captcha are saved here, so the bot will refuse to work without it. I advise you not to touch this.
***
### Installation
You can download the program   [HERE](https://github.com/STWonderFool/BombCrypto-Script/releases/tag/Releases) or download any Python environment and run "main.py"
from there.


### Maybe there will be something else..
