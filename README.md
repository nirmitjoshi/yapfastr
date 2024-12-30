## Setup

![demo](demo.gif)

1. **Clone the repo**  
   ```sh
   git clone https://github.com/nirmitjoshi/yapfastr.git
   cd yapfastr
   ```

2. **Install requirements**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up Twitter credentials**  
   Create a `.env` file in the root directory and add your Twitter API keys:
   ```
    TWITTER_CONSUMER_KEY=your_key
    TWITTER_CONSUMER_SECRET=your_secret
    TWITTER_ACCESS_TOKEN=your_token
    TWITTER_ACCESS_TOKEN_SECRET=your_secret_token
    TWITTER_VERIFIED=False  # Set to True for a verified account
   ```

4. **Run**
   ```sh
   python yapfastr.py
   ```
