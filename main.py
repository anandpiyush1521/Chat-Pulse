import streamlit as st  
from textblob import TextBlob
import pandas as pd
import altair as alt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns


# Fxn
def convert_to_df(sentiment):
	sentiment_dict = {'polarity':sentiment.polarity,'subjectivity':sentiment.subjectivity}
	sentiment_df = pd.DataFrame(sentiment_dict.items(),columns=['metric','value'])
	return sentiment_df

def analyze_token_sentiment(docx):
	analyzer = SentimentIntensityAnalyzer()
	pos_list = []
	neg_list = []
	neu_list = []
	for i in docx.split():
		res = analyzer.polarity_scores(i)['compound']
		if res > 0.1:
			pos_list.append(i)
			pos_list.append(res)

		elif res <= -0.1:
			neg_list.append(i)
			neg_list.append(res)
		else:
			neu_list.append(i)

	result = {'positives':pos_list,'negatives':neg_list,'neutral':neu_list}
	return result 


def main():
	#st.title("Sentiment Analysis NLP App")
	#st.subheader("Streamlit Projects")

	menu = ["Sentiment Analysis","Chat Analysis"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Sentiment Analysis":
		st.title("Sentiment Analysis NLP App")
		#st.subheader("Sentiment Analysis")
		with st.form(key='nlpForm'):
			raw_text = st.text_area("Enter Text Here")
			submit_button = st.form_submit_button(label='Analyze')

		# layout
		col1,col2 = st.columns(2)
		if submit_button:

			with col1:
				st.info("Results")
				sentiment = TextBlob(raw_text).sentiment
				st.write(sentiment)

				# Emoji
				if sentiment.polarity > 0:
					st.markdown("Sentiment:: Positive :smiley: ")
				elif sentiment.polarity < 0:
					st.markdown("Sentiment:: Negative :angry: ")
				else:
					st.markdown("Sentiment:: Neutral 😐 ")

				# Dataframe
				result_df = convert_to_df(sentiment)
				st.dataframe(result_df)

				# Visualization
				c = alt.Chart(result_df).mark_bar().encode(
					x='metric',
					y='value',
					color='metric')
				st.altair_chart(c,use_container_width=True)



			with col2:
				st.info("Token Sentiment")

				token_sentiments = analyze_token_sentiment(raw_text)
				st.write(token_sentiments)






	else:
		st.subheader("Chat Analysis")
		st.sidebar.title("Chat Analyzer")
		uploaded_file = st.file_uploader("choose File")
		if uploaded_file is not None:
			bytes_data = uploaded_file.getvalue()
			data = bytes_data.decode("utf-8")

			df = preprocessor.preprocess(data)
			st.dataframe(df)

			user_list = df['user'].unique().tolist()
			user_list.remove('group_notification')
			user_list.sort()
			user_list.insert(0, "Overall")
			selected_user = st.selectbox("Show analysis wrt", user_list)

			if st.button("Show Analysis"):
				
				st.title("Top statistics")
				num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
				col1, col2, col3, col4 = st.columns(4)
				with col1:
					st.header("Total Messages")
					st.title(num_messages)
				with col2:
					st.header("Total words")
					st.title(words)
				with col3:
					st.header("Media Shared")
					st.title(num_media_messages)
				with col4:
					st.header("Links Shared")
					st.title(num_links)
				
				st.title("Monthly Timeline")
				timeline = helper.monthly_timeline(selected_user, df)
				fig, ax = plt.subplots()
				ax.plot(timeline['time'], timeline['message'], color="red")
				plt.xticks(rotation="vertical")
				st.pyplot(fig)

				st.title("Daily Timeline")
				daily_timeline = helper.daily_timeline(selected_user, df)
				fig, ax = plt.subplots()
				ax.plot(daily_timeline['only_date'], daily_timeline['message'], color="yellow")
				plt.xticks(rotation="vertical")
				st.pyplot(fig)

				st.title("Activity Map")
				col1, col2 = st.columns(2)

				with col1:
					st.header("Most Busy Day")
					busy_day = helper.week_activity_map(selected_user, df)
					fig, ax = plt.subplots()
					ax.bar(busy_day.index, busy_day.values)
					plt.xticks(rotation='vertical')
					st.pyplot(fig)
				
				with col2:
					st.header("Most Busy Month")
					busy_month = helper.month_activity_map(selected_user, df)
					fig, ax = plt.subplots()
					ax.bar(busy_month.index, busy_month.values, color='pink')
					plt.xticks(rotation='vertical')
					st.pyplot(fig)

				
				st.title("Weekly activity heatmap")
				user_heatmap = helper.activity_heatmap(selected_user, df)
				fig, ax = plt.subplots()
				ax = sns.heatmap(user_heatmap)
				st.pyplot(fig)

				# Find the bussiest user in the group(group level)
				if selected_user == 'Overall':
					st.title('Most busy user')
					x, new_df = helper.most_busy_users(df)
					fig, ax = plt.subplots()
					col1, col2 = st.columns(2)

					with col1:
						ax.bar(x.index, x.values, color='green')
						plt.xticks(rotation = 'vertical')
						st.pyplot(fig)
					with col2:
						st.dataframe(new_df)
				

				# wordcloud
				st.title('WordCloud')
				df_wc = helper.create_wordcloud(selected_user, df)
				fig, ax = plt.subplots()
				ax.imshow(df_wc)
				st.pyplot(fig)


				# Most common words
				most_common_df = helper.most_common_words(selected_user, df)
				
				fig, ax = plt.subplots()
				ax.bar(most_common_df[0], most_common_df[1])

				# ax.barh(most_common_df[0], most_common_df[1])
				plt.xticks(rotation='vertical')
				
				st.title("Most common words")
				st.pyplot(fig)

				# st.dataframe(most_common_df)  # Dataframe

				# Emoji Analysis
				emoji_df = helper.emoji_helper(selected_user, df)
				st.title("Emoji Analysis")
				col1, col2 = st.columns(2)

				with col1:
					st.dataframe(emoji_df)
				with col2:
					fig, ax = plt.subplots()
					ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
					st.pyplot(fig)


if __name__ == '__main__':
	main()