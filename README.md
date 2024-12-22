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
   Add Your Twitter API Keys in `credentials.py`:
   ```python
   TWITTER_CREDENTIALS = {
       'consumer_key': 'your_key',
       'consumer_secret': 'your_secret',
       'access_token': 'your_token',
       'access_token_secret': 'your_secret_token',
       'verified': False  # Set to True for verified account
   }
   ```

4. **Run**
   ```sh
   python yapfastr.py
   ```
