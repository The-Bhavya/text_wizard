
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from pathlib import Path
import plotly.graph_objs as go
import plotly.express as px
from textblob import TextBlob
from pathlib import Path
from dputils.files import get_data
import os
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def summarize_text_from_file(file_path, summary_sentences=5, algorithm='lsa', language='english'):
    # Ensure file exists
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    # Read text from file
    text = get_data(path=file_path)
    if not text:
        return "⚠️ Data could not be extracted from the file"
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     text = file.read()
    # Initialize the parser
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)
    # Choose summarization algorithm
    if algorithm == 'lsa':
        summarizer = LsaSummarizer(stemmer)
    elif algorithm == 'lex_rank':
        summarizer = LexRankSummarizer(stemmer)
    elif algorithm == 'luhn':
        summarizer = LuhnSummarizer(stemmer)
    elif algorithm == 'text_rank':
        summarizer = TextRankSummarizer(stemmer)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    summarizer.stop_words = get_stop_words(language)
    # Summarize the text
    summary = summarizer(parser.document, summary_sentences)
    # Combine the summary sentences into a single string
    summary_text = " ".join([str(sentence) for sentence in summary])
    return summary_text

def allowed_file_type(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_sentiment_from_file(file_path):
    # Ensure the file exists
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read text from file
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     text = file.read()
    text = get_data(path=file_path)
    # Split text into sentences
    sentences = text.split('.')
    sentiments = []
    results = []
    # Analyze sentiment for each sentence
    for sentence in sentences:
        if sentence.strip():  # Skip empty sentences
            analysis = TextBlob(sentence)
            sentiments.append(analysis.sentiment.polarity)
            results.append((sentence, analysis.sentiment.polarity))
    # set theme to dark
    px.defaults.template = "plotly_dark"

    # Generate bar chart for sentence sentiment
    bar_chart = go.Figure(go.Bar(
        x=list(range(1, len(sentiments) + 1)),
        y=sentiments,
        text=[f'Sentence {i+1}: {sent}' for i, sent in enumerate(sentiments)],
        marker=dict(color=['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments])
    ))
    bar_chart.update_layout(
        title="Sentiment Analysis of Each Sentence",
        xaxis_title="Sentence Number",
        yaxis_title="Sentiment Polarity",
        yaxis=dict(range=[-1, 1]),
        showlegend=False,
        template = "plotly_dark"
    )
    

    # Overall sentiment pie chart
    positive = sum(1 for s in sentiments if s > 0)
    negative = sum(1 for s in sentiments if s < 0)
    neutral = sum(1 for s in sentiments if s == 0)

    overall_sentiment = {
        'Positive': positive,
        'Negative': negative,
        'Neutral': neutral
    }

    pie_chart = px.pie(
        names=list(overall_sentiment.keys()),
        values=list(overall_sentiment.values()),
        title="Overall Sentiment Distribution",
        hole=0.3
    )

    return bar_chart, pie_chart, results




if __name__ == "__main__":
    # print(allowed_file_type('file.txt'))  # True
    # print(allowed_file_type('file.pdf'))  # True
    # print(allowed_file_type('file.docx'))  # True
    # print(allowed_file_type('file.jpg'))  # False
    # print(allowed_file_type('file'))  # False
    # print(allowed_file_type('file.doc'))  # False
    # print(allowed_file_type('file.docx '))  # False

    out = summarize_text_from_file(
        'static/uploads/history.txt', summary_sentences=2, algorithm='lsa', language='english')
    print(out)
    

    file_path ='static/uploads/history.txt'  # Replace with your file path
    bar_chart, pie_chart = analyze_sentiment_from_file(file_path)
    # Show plots
    bar_chart.show()
    pie_chart.show()