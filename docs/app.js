document.addEventListener('DOMContentLoaded', () => {
  // --- Tab Navigation for Developer Guide ---
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');

      // Remove active from all buttons & panes
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      // Add active to current
      btn.classList.add('active');
      const targetPane = document.getElementById(`tab-${tabId}`);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });

  // --- Kindle Lookup Simulator ---
  const kindleWords = document.querySelectorAll('.kindle-word');
  const popup = document.getElementById('kindle-lookup-popup');
  const popupClose = document.getElementById('popup-close-btn');
  const popupWordTitle = document.getElementById('popup-word-title');
  const popupWordPos = document.getElementById('popup-word-pos');
  const popupWordDef = document.getElementById('popup-word-def');
  const popupDictSource = document.getElementById('popup-dict-source');

  // Hardcoded dictionary mappings for the simulator
  const dictionaryDb = {
    'benevolent': {
      pos: 'adj.',
      def: 'হিতৈষী, পরোপকারী, সদয়, দয়ালু, শুভাকাঙ্ক্ষী। Showing kindness or goodwill.',
      dict: 'Shobdo Vandar English-Bangla'
    },
    'literature': {
      pos: 'noun',
      def: 'সাহিত্য, সাহিত্যকর্ম, সুকুমার সাহিত্য। Written works, especially those considered of superior or lasting artistic merit.',
      dict: 'Shobdo Vandar English-Bangla'
    },
    'dictionary': {
      pos: 'noun',
      def: 'অভিধান, শব্দকোষ, শব্দার্থপুস্তক। A book or electronic resource that lists the words of a language and gives their meaning.',
      dict: 'Shobdo Vandar English-Bangla'
    },
    'হিতৈষী': {
      pos: 'বিণ.',
      def: 'benevolent, well-wishing, doing good to others. ব্যক্তি যে অপরের মঙ্গল বা হিত কামনা করে; শুভানুধ্যায়ী।',
      dict: 'Shobdo Vandar Bangla-English'
    },
    'অভিধান': {
      pos: 'বি.',
      def: 'dictionary, lexicon, vocabulary. শব্দার্থের পুস্তক, শব্দকোষ; যে গ্রন্থে শব্দের অর্থ, উৎস ও ব্যবহার সংকলিত থাকে।',
      dict: 'Shobdo Vandar Bangla-Bangla'
    }
  };

  kindleWords.forEach(wordEl => {
    wordEl.addEventListener('click', (e) => {
      const wordKey = wordEl.getAttribute('data-word');
      const definition = dictionaryDb[wordKey];

      if (definition) {
        popupWordTitle.textContent = wordKey;
        popupWordPos.textContent = `[${definition.pos}]`;
        popupWordDef.textContent = definition.def;
        popupDictSource.textContent = definition.dict;
        
        popup.style.display = 'block';
      }
      e.stopPropagation();
    });
  });

  // Close popup
  popupClose.addEventListener('click', () => {
    popup.style.display = 'none';
  });

  // Close popup if clicking outside the screen
  document.addEventListener('click', (e) => {
    if (popup.style.display === 'block' && !popup.contains(e.target) && !e.target.classList.contains('kindle-word')) {
      popup.style.display = 'none';
    }
  });


  // --- GitHub API Integration ---
  const repoOwner = 'tahmidxp96';
  const repoName = 'Shobdo-Vandar';
  const apiEndpoint = `https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`;

  const releaseStatusText = document.getElementById('release-status-text');
  const releaseMetaContainer = document.getElementById('release-meta-container');
  const releaseVerTag = document.getElementById('release-ver-tag');
  const releaseDateEl = document.getElementById('release-date');

  // DOM references for download buttons
  const dlEnBnBtn = document.getElementById('dl-en-bn');
  const dlBnEnBtn = document.getElementById('dl-bn-en');
  const dlBnBnBtn = document.getElementById('dl-bn-bn');

  // Fallback version static assets (used if API fails or rate-limits)
  const defaultVersion = 'v1.5.2';

  function formatGitHubDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
  }

  function formatBytesToMB(bytes) {
    if (!bytes) return null;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  // Attempt to fetch latest release metadata
  fetch(apiEndpoint)
    .then(response => {
      if (!response.ok) {
        throw new Error(`GitHub API returned status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const tagName = data.tag_name;
      const publishedAt = data.published_at;
      const formattedDate = formatGitHubDate(publishedAt);

      // Update Release Info Bar
      releaseStatusText.innerHTML = `🟢 Live connection established.`;
      releaseVerTag.textContent = tagName;
      releaseDateEl.textContent = formattedDate;
      releaseMetaContainer.style.display = 'block';

      // Look through release assets to update download buttons with exact URLs and sizes
      let enBnFound = false;
      let bnEnFound = false;
      let bnBnFound = false;

      if (data.assets && data.assets.length > 0) {
        data.assets.forEach(asset => {
          const name = asset.name;
          const url = asset.browser_download_url;
          const sizeMB = formatBytesToMB(asset.size);

          if (name.includes('en-bn') && name.endsWith('.mobi')) {
            dlEnBnBtn.href = url;
            if (sizeMB) {
              const sizeLabel = dlEnBnBtn.closest('.download-card').querySelector('.stat-val:nth-child(2)');
              // Let's find the specific stat-item containing file size
              const cardStats = dlEnBnBtn.closest('.download-card').querySelectorAll('.stat-item');
              cardStats.forEach(stat => {
                if (stat.querySelector('.stat-label').textContent.toUpperCase().includes('SIZE')) {
                  stat.querySelector('.stat-val').textContent = `~${sizeMB}`;
                }
              });
            }
            enBnFound = true;
          } else if (name.includes('bn-en') && name.endsWith('.mobi')) {
            dlBnEnBtn.href = url;
            if (sizeMB) {
              const cardStats = dlBnEnBtn.closest('.download-card').querySelectorAll('.stat-item');
              cardStats.forEach(stat => {
                if (stat.querySelector('.stat-label').textContent.toUpperCase().includes('SIZE')) {
                  stat.querySelector('.stat-val').textContent = `~${sizeMB}`;
                }
              });
            }
            bnEnFound = true;
          } else if (name.includes('bn-bn') && name.endsWith('.mobi')) {
            dlBnBnBtn.href = url;
            if (sizeMB) {
              const cardStats = dlBnBnBtn.closest('.download-card').querySelectorAll('.stat-item');
              cardStats.forEach(stat => {
                if (stat.querySelector('.stat-label').textContent.toUpperCase().includes('SIZE')) {
                  stat.querySelector('.stat-val').textContent = `~${sizeMB}`;
                }
              });
            }
            bnBnFound = true;
          }
        });
      }

      console.log(`GitHub release API parsed successfully. Version loaded: ${tagName}`);
    })
    .catch(error => {
      console.warn('Could not fetch latest release info from GitHub API. Falling back to default links.', error);
      
      // Fallback UI
      releaseStatusText.innerHTML = `🟡 Offline/Cached Mode.`;
      releaseVerTag.textContent = defaultVersion;
      releaseDateEl.textContent = 'July 2026';
      releaseMetaContainer.style.display = 'block';
    });
});
