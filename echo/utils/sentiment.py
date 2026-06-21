import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        """Returns the polarity scores of the text."""
        return self.sia.polarity_scores(text)

    def analyze_sentences(self, text):
        """Analyzes text sentence by sentence."""
        sentences = text.split(".")
        results = []
        for sentence in sentences:
            stripped = sentence.strip()
            if stripped:
                results.append((stripped, self.sia.polarity_scores(stripped)))
        return results

    def create_sentiment_chart(self, overall_scores, username, output_path="sentiment_chart.png"):
        categories = list(overall_scores.keys())
        scores = list(overall_scores.values())

        plt.figure(figsize=(6, 4))
        plt.bar(categories, scores, color=["green", "blue", "red", "purple"])
        plt.title(f"Sentiment Distribution for {username}")
        plt.ylabel("Score")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    def generate_report(self, selected_text, username, user_id, save_to_db_callback):
        sentence_results = self.analyze_sentences(selected_text)
        if not sentence_results:
            return None

        # Calculate overall scores
        scores = [res[1] for res in sentence_results]
        overall_scores = {
            "Positive": sum(score["pos"] for score in scores) / len(scores),
            "Neutral": sum(score["neu"] for score in scores) / len(scores),
            "Negative": sum(score["neg"] for score in scores) / len(scores),
            "Compound": sum(score["compound"] for score in scores) / len(scores),
        }

        # Save temporary chart
        chart_path = "sentiment_chart.png"
        self.create_sentiment_chart(overall_scores, username, output_path=chart_path)

        # Sanitize the filename
        sanitized_text = selected_text[:20]
        sanitized_text = "".join(c if c.isalnum() or c.isspace() else "" for c in sanitized_text)
        sanitized_text = sanitized_text.replace(" ", "_")
        if not sanitized_text:
            sanitized_text = "default_report"
        report_name = f"{sanitized_text}_sentiment_report.pdf"

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt=f"Sentiment Analysis Report for {username}", ln=True, align="C")
        pdf.ln(10)

        # Overall Scores
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt="Overall Sentiment Scores:", ln=True)
        for category, score in overall_scores.items():
            pdf.cell(0, 10, txt=f"  {category}: {score:.2f}", ln=True)
        pdf.ln(10)

        # Sentence-level analysis
        pdf.cell(0, 10, txt="Sentence-level Sentiment Analysis:", ln=True)
        for sentence, score in sentence_results:
            pdf.multi_cell(0, 10, txt=f"  {sentence}")
            pdf.cell(0, 10, txt=f"    Positive: {score['pos']:.2f}, Neutral: {score['neu']:.2f}, Negative: {score['neg']:.2f}, Compound: {score['compound']:.2f}", ln=True)

        # Add chart
        pdf.add_page()
        pdf.image(chart_path, x=10, y=10, w=180)
        pdf.ln(90)

        # Save the report
        user_folder = os.path.join("users", username)
        os.makedirs(user_folder, exist_ok=True)
        report_path = os.path.join(user_folder, report_name)
        pdf.output(report_path)

        # Save to DB
        save_to_db_callback(user_id, report_name, report_path)

        # Clean up temporary chart file if exists
        try:
            if os.path.exists(chart_path):
                os.remove(chart_path)
        except Exception as e:
            print(f"Failed to delete temp chart: {e}")

        return report_path
