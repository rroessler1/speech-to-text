This is an Anki addon, NOT a standalone Python program. You can add it to Anki as a regular plug-in, go here: https://ankiweb.net/shared/info/673333980

<b>Plugin Info</b>

This add-on tests your pronunciation by recording your voice, analyzing it using a Speech-to-Text (STT) service, and then comparing it with the value on the current card.

It currently supports Google and Microsoft Cloud Speech-to-Text services.

<b>HOW TO USE</b>

You need either a Google or Microsoft API key, which may cost money, but Microsoft has a very generous free tier. Here are instructions for both:

<b>Google</b>

Follow the instructions here: <a href="https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries" rel="nofollow">https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries</a>, which are summarized below.

Basically,

1.1. Go here: <a href="https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries" rel="nofollow">https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries</a> and click the "Set up a Project" button.

1.2. Follow the steps to create a project and add a payment method.

2. Create an API Key.  (Google will automatically generate a "Service Account Key" but this is not what you want.)

2.1. Go to the developers console: <a href="https://console.developers.google.com/" rel="nofollow">https://console.developers.google.com/</a>

2.2. Click on "Credentials"

2.3. Click on "Create Credentials -&gt; API Key" and copy the value.

<b>Microsoft</b>

1. Create a Microsoft Portal Account http://portal.azure.com

2. Create a "Speech" by Microsoft resource here: https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices
(None of the naming / settings are particularly important)

3. Once that's done, click on "Go to Resource"

4. Click on "Keys and Endpoint"

5. Click on "Show Keys". These are your two API keys. Use either.

6. Take note of "location", you'll need it in the configuration.

<b>Once You Have an API Key</b>

Install this add-on, then configure it in Anki.  Go to Tools -&gt; Test Your Pronunciation Settings

1. Select which service you will use (Google or Microsoft)

2. Enter the API Key you created above.

2.1 If using Microsoft, you also need to select the API location (explained above).

3. Choose which language you will be pronouncing.

4. Enter the Field Name you will read. This is used to compare your voice to the actual value on the card.
(If you are unfamiliar with Anki fields it is the number one feature you should understand, check it out here: <a href="https://docs.ankiweb.net/#/getting-started?id=notes-amp-fields" rel="nofollow">https://docs.ankiweb.net/#/getting-started?id=notes-amp-fields</a> )

5. Whenever you study a card, you can go to "Tools -&gt; Test Your Pronunciation" (or press Ctrl + Shift + S) to activate the plugin. Record your voice and then view the results.

<b>Cloud Speech-to-Text Pricing</b>

Please note this is the price charged by Google and Microsoft to use their Cloud Speech-to-Text services, and is completely out of my control.

<b>Google</b>

The current pricing details are here: <a href="https://cloud.google.com/speech-to-text/pricing" rel="nofollow">https://cloud.google.com/speech-to-text/pricing</a>

The first 60 minutes per month are free, and then it's $0.004 or $0.006 USD per 15 seconds (rounded up at 15 second increments), depending on if you enable data logging.

If you test your pronunciation on 100 cards every day (and each audio clip is 15 seconds or less), then it will cost you:
(3000 cards per month - 240 (free tier)) * $0.006 = $16.56 USD / month.  Or $11.04 if you enable data logging.

<b>Microsoft</b>

Pricing details are here: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/

On the Free Tier, you get 5 free hours of audio. If you use more than this, you have to manually upgrade to the standard tier, which costs $1 per hour.

If you test your pronunciation on 100 cards every day, and the average clip length is 6 seconds, then it will be <b>Free</b>.

If the average clip length is 15 seconds, it will cost you $7.50 USD per month.

30 days * 100 cards * 15 seconds / 3600 seconds in an hour = 12.5 hours - 5 free hours = $7.50 USD

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

<b>Note on Speech-to-Text Accuracy, especially with Chinese</b>

How accurate is Speech-to-Text?

I initially developed this plugin to help me practice Chinese; I'm a beginner learner and my pronunciation is quite bad, something many learners struggle with.

Olle over at Hacking Chinese did a not-statistically-significant analysis, and found that Google's Chinese Speech-to-Text is basically perfect: <a href="https://www.hackingchinese.com/using-speech-recognition-to-improve-chinese-pronunciation-part-1/" rel="nofollow">https://www.hackingchinese.com/using-speech-recognition-to-improve-chinese-pronunciation-part-1/</a>

My Chinese friends (again, not statistically significant) also report that Google "always" gets their Chinese dictation correct.

This initially seems impossible given the "difficulty" of Chinese pronunciation, but if you think again it intuitively makes sense. The tones, while difficult for foreigners unfamiliar with tonal languages, provide an extra signal for the algorithm that makes it easier to identify the syllable/word. Native speakers who can produce this perfectly see accurate results.

Now of course, even if you don't say things perfectly, the algorithm tries to figure it out. So a reasonable conclusion is that: <b>If the computer thinks you said it wrong, you did, but if the computer thinks you said it right, it still might sound weird to a native.</b> At least for Chinese (and presumably other tonal languages, though I haven't checked).

What about for other languages?

Well, Google is certainly not 100% accurate when I do Speech-to-Text for English, but if I speak a bit slow and clearly, I would say it's quite good.

<b>Issues / Feedback</b>

Please submit any issues on Github: <a href="https://github.com/rroessler1/speech-to-text" rel="nofollow">https://github.com/rroessler1/speech-to-text</a>

<b>Donate</b>

If you find my work helpful, I would be honored with any kind of donation, as it does take a very surprisingly long time to develop software available for public use.

<a href="https://www.paypal.com/donate?hosted_button_id=5SMQLVSC5XA5W" rel="nofollow">https://www.paypal.com/donate?hosted_button_id=5SMQLVSC5XA5W</a>

If you like it, please comment here or send me feedback!