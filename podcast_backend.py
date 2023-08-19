import modal

def download_whisper():
  # Load the Whisper model
  import os
  import whisper
  print ("Download the Whisper model")

  # Perform download only once and save to Container storage
  whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("corise-podcast-project")
corise_image = modal.Image.debian_slim().pip_install("feedparser",
                                                     "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                                     "requests",
                                                     "ffmpeg",
                                                     "openai",
                                                     "tiktoken",
                                                     "wikipedia",
                                                     "ffmpeg-python").apt_install("ffmpeg").run_function(download_whisper)

@stub.function(image=corise_image, gpu="any", timeout=600)
def get_transcribe_podcast(rss_url, local_path):
  print ("Starting Podcast Transcription Function")
  print ("Feed URL: ", rss_url)
  print ("Local Path:", local_path)

  # Read from the RSS Feed URL
  import feedparser
  intelligence_feed = feedparser.parse(rss_url)
  podcast_title = intelligence_feed['feed']['title']
  episode_title = intelligence_feed.entries[0]['title']
  episode_image = intelligence_feed['feed']['image'].href
  for item in intelligence_feed.entries[0].links:
    if (item['type'] == 'audio/mpeg'):
      episode_url = item.href
  episode_name = "podcast_episode.mp3"
  print ("RSS URL read and episode URL: ", episode_url)

  # Download the podcast episode by parsing the RSS feed
  from pathlib import Path
  p = Path(local_path)
  p.mkdir(exist_ok=True)

  print ("Downloading the podcast episode")
  import requests
  with requests.get(episode_url, stream=True) as r:
    r.raise_for_status()
    episode_path = p.joinpath(episode_name)
    with open(episode_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

  print ("Podcast Episode downloaded")

  # Load the Whisper model
  import os
  import whisper

  # Load model from saved location
  print ("Load the Whisper model")
  model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')

  # Perform the transcription
  print ("Starting podcast transcription")
  result = model.transcribe(local_path + episode_name)

  # Return the transcribed text
  print ("Podcast transcription completed, returning results...")
  output = {}
  output['podcast_title'] = podcast_title
  output['episode_title'] = episode_title
  output['episode_image'] = episode_image
  output['episode_transcript'] = result['text']
  return output

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_info(podcast_transcript):
  import openai

  instructPrompt = """
    Information: You will be provided with a text document, which is essentially transcibed from a rock music podcast.

    Role: You are an experienced copywriter who excels at giving byte sized summary of the transcriptions which is easily digestable.

    Instruction: You must try to provide the following answers from the given text information:-
        1. A well thought out summary of the transcription.
        2. Who is the host of the podcast
        3. When was the podcast published (if mentioned)
        4. If there is a single or multiple guests, please list their names down in a comma separated format.
        5. If they are discussing a/multiple music artist and/or any album by them, please extract that info too.
        6. Give your commentary about the subject at hand too.
        7. Identify the tone of the discussion as well.
        8. What were the highlights of the podcast.

    Please note that the output should be in a JSON formatted document. I do not want to compromise on that.
    Also, please do not give me anything else in the output apart from the JSON.

    Input format:
        Input : " Hi, my name is ....."

    Output format expected:
        Output :
          {"summary": "...",
          "host_name": "...",
          "date_published": "...",
          "guests":["...", "...",...],
          "artists_discussed":{"artist_name":["song_name/album_name",...],...},
          "commentry":"...",
          "tone":"...",
          "highlights":"..."}

    ---------------------------------------
    Input :
  """

  request = instructPrompt + podcast_transcript

  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                              messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                        {"role": "user", "content": request}
                                                        ]
                                              )

  podcastInfo = chatOutput.choices[0].message.content

  return podcastInfo

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200)
def process_podcast(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.call(url, path)
  podcast_info = get_podcast_info.call(podcast_details['episode_transcript'])
  output['podcast_details'] = podcast_details
  output['podcast_info'] = podcast_info
  return output

@stub.local_entrypoint()
def test_method(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.call(url, path)
  print ("Podcast Info: ", get_podcast_info.call(podcast_details['episode_transcript']))
