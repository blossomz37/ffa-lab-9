function safeGetLastUserPlainText(authorizedResources) {
  if (!authorizedResources || !authorizedResources.lastUserMessage) return null;
  const content = authorizedResources.lastUserMessage.content;
  if (!Array.isArray(content)) return null;
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

function nowMs() {
  if (typeof performance !== 'undefined' && performance && typeof performance.now === 'function') {
    return performance.now();
  }
  return Date.now();
}

function computeStats(rawText, wordsPerPage, computeReadability) {
  const start = nowMs();
  const text = (rawText || '').replace(/\r\n?/g, '\n');
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      words: 0, sentences: 0, complexSentences: 0, paragraphs: 0, pages: 0, readability: 0,
      avgWordsPerSentence: 0, avgSyllablesPerWord: 0, processingMs: Math.round(nowMs() - start)
    };
  }
  const wordsArr = trimmed.split(/\s+/).filter(w => w.length > 0);
  const words = wordsArr.length;
  const sentenceEndings = trimmed.match(/[.!?]+/g) || [];
  const sentences = sentenceEndings.length || (words > 0 ? 1 : 0);
  const paragraphArr = trimmed.split(/\n\s*\n/).filter(p => p.trim().length > 0);
  const paragraphs = paragraphArr.length;
  const pages = words === 0 ? 0 : Math.ceil(words / Math.max(1, wordsPerPage));
  const sentenceTexts = trimmed.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const complexSentences = sentenceTexts.filter(s => {
    const lower = s.toLowerCase();
    return /,|;/.test(lower) || /\(and|but|or|nor|for|so|yet|because|although|since|while|if|unless|when|where|whereas)\/.test(lower);
  }).length;
  let totalSyllables = 0;
  for (const w of wordsArr) totalSyllables += countSyllables(w.replace(/[^a-zA-Z]/g, ''));
  const avgWordsPerSentence = sentences > 0 ? words / sentences : 0;
  const avgSyllablesPerWord = words > 0 ? totalSyllables / words : 0;
  let readability = 0;
  if (computeReadability && words > 0 && sentences > 0) {
    readability = Math.round(206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord));
    readability = Math.max(0, Math.min(100, readability));
  }
  return {
    words, sentences, complexSentences, paragraphs, pages, readability,
    avgWordsPerSentence: Number(avgWordsPerSentence.toFixed(2)),
    avgSyllablesPerWord: Number(avgSyllablesPerWord.toFixed(3)),
    processingMs: Math.round(nowMs() - start)
  };
}

async function document_stats_ai(params, userSettings, authorizedResources) {
  const explicitText = params && typeof params.text === 'string' ? params.text : null;
  const fallback = safeGetLastUserPlainText(authorizedResources);
  const source = explicitText ? 'parameter:text' : (fallback ? 'last_user_message' : 'none');
  const textToAnalyze = explicitText || fallback || '';
  const wordsPerPageSetting = Number(userSettings?.words_per_page) || 250;
  const computeReadability = (userSettings?.enable_readability !== 'No');
  const stats = computeStats(textToAnalyze, wordsPerPageSetting, computeReadability);
  const responseFormat = (params && typeof params.response_format === 'string') ? params.response_format : 'markdown';
  const includePreviews = !!(params && params.include_previews === true);

  const meta = {
    source, wordsPerPage: wordsPerPageSetting, readabilityComputed: computeReadability
  };

  // Lightweight tips the assistant can weave into its summary
  const suggestions = [];
  if (stats.avgWordsPerSentence > 25) suggestions.push('Consider shortening sentences for clarity.');
  if (stats.readability && stats.readability < 50) suggestions.push('Reading ease is low; simplify vocabulary or structure.');
  if (stats.complexSentences > Math.max(1, Math.round(stats.sentences * 0.3))) suggestions.push('There are many complex sentences; vary sentence length.');

  const previews = {};
  if (includePreviews) {
    const lines = [
      '# Document Statistics',
      `- Words: ${stats.words.toLocaleString()}`,
      `- Sentences: ${stats.sentences.toLocaleString()}`,
      `- Complex Sentences: ${stats.complexSentences.toLocaleString()}`,
      `- Paragraphs: ${stats.paragraphs.toLocaleString()}`,
      `- Estimated Pages (@${wordsPerPageSetting} wpp): ${stats.pages.toLocaleString()}`,
      `- Avg Words/Sentence: ${stats.avgWordsPerSentence}`,
      `- Avg Syllables/Word: ${stats.avgSyllablesPerWord}`,
      `- Readability (Flesch 0-100): ${computeReadability ? stats.readability : 'Skipped'}`,
      `- Source: ${source}`
    ];
    previews.markdown = lines.join('\n');
    previews.html = `<div><h2>Document Statistics</h2><ul>
<li><b>Words:</b> ${stats.words.toLocaleString()}</li>
<li><b>Sentences:</b> ${stats.sentences.toLocaleString()}</li>
<li><b>Complex Sentences:</b> ${stats.complexSentences.toLocaleString()}</li>
<li><b>Paragraphs:</b> ${stats.paragraphs.toLocaleString()}</li>
<li><b>Estimated Pages (@${wordsPerPageSetting} wpp):</b> ${stats.pages.toLocaleString()}</li>
<li><b>Avg Words/Sentence:</b> ${stats.avgWordsPerSentence}</li>
<li><b>Avg Syllables/Word:</b> ${stats.avgSyllablesPerWord}</li>
<li><b>Readability (Flesch 0-100):</b> ${computeReadability ? stats.readability : 'Skipped'}</li>
<li><b>Source:</b> ${source}</li>
</ul></div>`;
  }

  return {
    stats, meta, suggestions, responseFormat, previews
  };
}