function safeGetLastUserPlainText(authorizedResources) {
  if (!authorizedResources || !authorizedResources.lastUserMessage) return null;
  const content = authorizedResources.lastUserMessage.content;
  if (!Array.isArray(content)) return null;
  // Find first text segment
  for (const item of content) {
    if (item && (item.type === 'text' || item.type === 'plain_text')) {
      if (typeof item.text === 'string') return item.text;
      if (typeof item.plain_text === 'string') return item.plain_text;
      if (typeof item.value === 'string') return item.value;
    }
  }
  return null;
}

function countSyllables(word) {
  if (!word) return 0;
  word = word.toLowerCase();
  if (word.length <= 3) return 1;
  word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/i, '');
  word = word.replace(/^y/, '');
  const matches = word.match(/[aeiouy]{1,2}/g);
  return matches ? matches.length : 1;
}

function computeStats(rawText, wordsPerPage) {
  const start = performance.now();
  const text = (rawText || '').replace(/\r\n?/g, '\n');
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      words: 0,
      sentences: 0,
      complexSentences: 0,
      paragraphs: 0,
      pages: 0,
      readability: 0,
      processingMs: Math.round(performance.now() - start)
    };
  }

  const wordsArr = trimmed.split(/\s+/).filter(w => w.length > 0);
  const words = wordsArr.length;
  const sentenceEndings = trimmed.match(/[.!?]+/g) || [];
  const sentences = sentenceEndings.length || (words > 0 ? 1 : 0);
  const paragraphArr = trimmed.split(/\n\s*\n/).filter(p => p.trim().length > 0);
  const paragraphs = paragraphArr.length;
  const pages = words === 0 ? 0 : Math.ceil(words / Math.max(1, wordsPerPage));

  // Complex sentence heuristic
  const sentenceTexts = trimmed.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const complexSentences = sentenceTexts.filter(s => {
    const lower = s.toLowerCase();
    return /,|;/.test(lower) || /\b(and|but|or|nor|for|so|yet|because|although|since|while|if|unless|when|where|whereas)\b/.test(lower);
  }).length;

  // Syllables
  let totalSyllables = 0;
  for (const w of wordsArr) {
    totalSyllables += countSyllables(w.replace(/[^a-zA-Z]/g, ''));
  }
  let readability = 0;
  if (words > 0 && sentences > 0) {
    const avgWordsPerSentence = words / sentences;
    const avgSyllablesPerWord = totalSyllables / words;
    readability = Math.round(206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord));
    readability = Math.max(0, Math.min(100, readability));
  }

  return {
    words,
    sentences,
    complexSentences,
    paragraphs,
    pages,
    readability,
    processingMs: Math.round(performance.now() - start)
  };
}

async function document_stats(params, userSettings, authorizedResources) {
  const explicitText = params && typeof params.text === 'string' ? params.text : null;
  const fallback = safeGetLastUserPlainText(authorizedResources);
  const source = explicitText ? 'parameter:text' : (fallback ? 'last_user_message' : 'none');
  const textToAnalyze = explicitText || fallback || '';

  const wordsPerPageSetting = Number(userSettings?.words_per_page) || 250;
  const stats = computeStats(textToAnalyze, wordsPerPageSetting);

  if (source === 'none') {
    return {
      cards: [
        {
            type: 'text',
            text: 'No text provided and no last user message text content was found. Provide a `text` parameter or send a message first.'
        }
      ]
    };
  }

  const lines = [
    'Document Statistics',
    '-------------------',
    `Words: ${stats.words.toLocaleString()}`,
    `Sentences: ${stats.sentences.toLocaleString()}`,
    `Complex Sentences: ${stats.complexSentences.toLocaleString()}`,
    `Paragraphs: ${stats.paragraphs.toLocaleString()}`,
    `Estimated Pages (@${wordsPerPageSetting} wpp): ${stats.pages.toLocaleString()}`,
    `Readability (Flesch 0-100): ${stats.readability}`,
    `Processing Time: ${stats.processingMs} ms`,
    `Source: ${source}`
  ];

  const cards = [
    {
      type: 'text',
      text: lines.join('\n')
    }
  ];

  if (userSettings?.return_json_card === 'Yes') {
    cards.push({
      type: 'text',
      text: 'Raw JSON:\n' + JSON.stringify({ ...stats, source, wordsPerPage: wordsPerPageSetting }, null, 2)
    });
  }

  return { cards };
}
