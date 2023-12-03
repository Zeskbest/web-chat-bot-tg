Install PhantomJS
---

[src](https://www.programsbuzz.com/article/install-phantomjs-ubuntu-1804)

1. install deps 

   ```bash
   sudo apt-get update
   sudo apt-get install build-essential chrpath libssl-dev libxft-dev -y
   sudo apt-get install libfreetype6 libfreetype6-dev -y
   sudo apt-get install libfontconfig1 libfontconfig1-dev -y
   ```
2. Get PhantomJS
   ```bash
   export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
   wget "https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2"
   tar xvjf $PHANTOM_JS.tar.bz2
   ```
3. Install system-wide
    ```bash
    sudo mv $PHANTOM_JS /usr/local/share
    sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
    OPENSSL_CONF=/etc/ssl/ phantomjs --version
    ```
