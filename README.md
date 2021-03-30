This is an Anki addon, NOT a standalone Python program. You can add it to Anki as a regular plug-in, go here: https://ankiweb.net/shared/info/673333980

<b>Plugin Info</b>

This add-on tests your pronunciation by recording your voice, analyzing it using Google Speech-to-Text (STT), and then comparing it with the value on the current card.

<b>HOW TO USE</b>

1. You need a Google Speech-to-Text API Key. Follow the instructions here: <a href="https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries" rel="nofollow">https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries</a>

Basically,

1.1. Go here: <a href="https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries" rel="nofollow">https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries</a> and click the "Set up a Project" button.

1.2. Follow the steps to create a project and add a payment method.

2. Create an API Key.  (Google will automatically generate a "Service Account Key" but this is not what you want.)

2.1. Go to the developers console: <a href="https://console.developers.google.com/" rel="nofollow">https://console.developers.google.com/</a>

2.2. Click on "Credentials"

2.3. Click on "Create Credentials -&gt; API Key" and copy the value.

3. Once you install this add-on, configure it in Anki.  Go to Tools -&gt; Test Your Pronunciation Settings

3.1. Enter the API Key you created above.

3.2. Choose which language you will be reading.

3.3. Enter the Field Name you will read. This is used to compare your voice to the actual value on the card.
(If you are unfamiliar with Anki fields it is the number one feature you should understand, check it out here: <a href="https://docs.ankiweb.net/#/getting-started?id=notes-amp-fields" rel="nofollow">https://docs.ankiweb.net/#/getting-started?id=notes-amp-fields</a> )

4. Whenever you study a card, you can go to "Tools -&gt; Test Your Pronunciation" (or press Ctrl + Shift + S) to activate the plugin. Record your voice and then view the results.

<b>Google Speech-to-Text Pricing</b>

The current pricing details are here: <a href="https://cloud.google.com/speech-to-text/pricing" rel="nofollow">https://cloud.google.com/speech-to-text/pricing</a>

Currently, the first 60 minutes per month are free, and then it's $0.004 or $0.006 USD per 15 seconds, depending on if you enable data logging.

If you test your pronunciation on 100 cards every day (and each audio clip is 15 seconds or less), then it will cost you:
(3000 cards per month - 240 (free tier)) * $0.006 = $16.56 USD / month.  Or $11.04 if you enable data logging.

Unfortunately, this is obviously out of my control. But you can choose when to test your pronunciation, so you can choose to only test it a few times a day if you prefer.

At least, it is exponentially cheaper than hiring a tutor.

<b>Note on Speech-to-Text Accuracy, especially with Chinese</b>

How accurate is Speech-to-Text?

I initially developed this plugin to help me practice Chinese; I'm a beginner learner and my pronunciation is quite bad, something many learners struggle with.

Olle over at Hacking Chinese did a not-statistically-significant analysis, and found that Google's Chinese Speech-to-Text is basically perfect: <a href="https://www.hackingchinese.com/using-speech-recognition-to-improve-chinese-pronunciation-part-1/" rel="nofollow">https://www.hackingchinese.com/using-speech-recognition-to-improve-chinese-pronunciation-part-1/</a>

My Chinese friends (again, not statistically significant) also report that Google "always" gets their Chinese dictation correct.

This initially seems impossible given the "difficulty" of Chinese pronunciation, but if you think again it intuitively makes sense. The tones, while difficult for foreigners unfamiliar with tonal languages, provide an extra signal for the algorithm that makes it easier to identify the syllable/word. Native speakers who can produce this perfectly see accurate results.

Now of course, even if you don't say things perfectly, the algorithm tries to figure it out. So a reasonable conclusion is that: <b>If the computer thinks you said it wrong, you did, but if the computer thinks you said it right, it still might sound weird to a native.</b> At least for Chinese (and presumably other tonal languages, though I haven't checked).

What about for other languages?

Well, Google is certainly not 100% accurate when I do Speech-to-Text for English, but if I speak a bit slow and clearly, I would say it's quite good.

<b>Punctuation</b>

The plugin ignores punctuation when analyzing the card and your speech, so if the card reads:
"Hello! How are you?"
You can say "Hello how are you" and it will be correct.
(You can also say "Hello exclamation mark how are you question mark", and that will work too.)

But one limitation of this is that decimal points are also removed, so if the card reads:
"3.5"
You can say "Three point five" or "Thirty-five", and both will be marked as correct

<b>Using this with Chinese</b>

This plugin will show your results in Pinyin, to make it easier for beginners to see what they got wrong, and whether it was a tone issue or not.

<b>Issues / Feedback</b>

Please submit any issues on Github: <a href="https://github.com/rroessler1/speech-to-text" rel="nofollow">https://github.com/rroessler1/speech-to-text</a>

<b>Donate</b>

If you find my work helpful, I would be honored with any kind of donation, as it does take a very surprisingly long time to develop software available for public use.

<a href="https://www.paypal.com/donate?hosted_button_id=5SMQLVSC5XA5W" rel="nofollow">https://www.paypal.com/donate?hosted_button_id=5SMQLVSC5XA5W</a>

If you like it, please comment here or send me feedback!