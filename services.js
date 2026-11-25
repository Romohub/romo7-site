/* Project briefs stay on the visitor's device. */
(() => {
  'use strict';
  const form = document.getElementById('serviceBriefForm');
  if (!form) return;
  const output = document.getElementById('preparedBrief');
  const status = document.getElementById('briefStatus');
  const fa = () => document.documentElement.lang === 'fa';
  const say = (en, persian) => fa() ? persian : en;
  const allowedServices = new Set(['research','localization','video','ai_qa','ai_ads','other']);
  const requestedService = new URLSearchParams(window.location.search).get('service');
  if (allowedServices.has(requestedService)) {
    form.elements.service.value = requestedService;
  }
  document.querySelectorAll('.service-request-link').forEach(link => {
    link.addEventListener('click', () => {
      if (allowedServices.has(link.dataset.service)) form.elements.service.value = link.dataset.service;
    });
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const input = form.elements.input;
    input.setCustomValidity('');
    if (input.value && !/^https?:\/\//i.test(input.value)) {
      input.setCustomValidity(say('Use a public HTTP or HTTPS link.', 'یک لینک عمومی با http یا https وارد کن.'));
    }
    if (!form.reportValidity()) return;
    const field = name => form.elements[name].value.trim();
    const selected = form.elements.service.selectedOptions[0].textContent;
    const lines = [say('Romo7 project brief', 'شرح کار برای Romo7'),
      say('Service: ', 'خدمت: ') + selected,
      say('Desired outcome: ', 'خروجی‌ای که می‌خواهم: ') + field('question')];
    if (field('input')) lines.push(say('Public input: ', 'لینک ورودی: ') + field('input'));
    if (field('budget')) lines.push(say('Proposed budget: ', 'بودجه پیشنهادی: ') + field('budget') + ' ' + field('currency'));
    if (field('deadline')) lines.push(say('Desired deadline: ', 'زمان تحویل دلخواه: ') + field('deadline'));
    lines.push(say('Please confirm scope, availability and payment terms before starting.', 'لطفاً قبل از شروع، محدوده کار، امکان انجام و شرایط پرداخت را تأیید کنید.'));
    output.value = lines.join('\n\n');
    document.getElementById('briefResult').hidden = false;
    status.textContent = say('Prepared locally; nothing sent. Opening the GitHub request form will also try to copy this brief for you. Paste only non-confidential content, or use Copy brief first.', 'متن روی دستگاه آماده شد و چیزی ارسال نشده است. اگر فرم GitHub را باز کنی، تلاش می‌کنم متن را کپی کنم؛ فقط اطلاعات غیرمحرمانه را وارد کن یا اول دکمه کپی را بزن.');
    output.focus();
  });
  const publicRequestLink = document.querySelector('#briefResult a[href*="issues/new?template=collaboration.yml"]');
  if (publicRequestLink) {
    // A user click opens GitHub as before. Copy only the already-prepared
    // local text, never auto-submit a public issue or transmit form fields.
    publicRequestLink.addEventListener('click', () => {
      if (!output.value) return;
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        status.textContent = say('Clipboard unavailable: use Copy brief, then paste into GitHub.', 'کلیپ‌بورد در دسترس نیست؛ متن را کپی کن و در GitHub بچسبان.');
        return;
      }
      navigator.clipboard.writeText(output.value).then(() => {
        status.textContent = say('Brief copied; paste it into the GitHub request form. Nothing was submitted automatically.', 'متن کپی شد؛ در فرم GitHub بچسبانش. چیزی خودکار ارسال نشد.');
      }).catch(() => {
        status.textContent = say('Auto-copy was blocked by the browser; use Copy brief and paste manually.', 'مرورگر کپی خودکار را قبول نکرد؛ از دکمه کپی استفاده کن.');
      });
    });
  }
  document.getElementById('copyBrief').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(output.value);
      status.textContent = say('Copied. Open the public GitHub form and paste only non-confidential information; or start privately on X.', 'کپی شد. فرم عمومی GitHub را باز کن و فقط متن غیرمحرمانه را بچسبان؛ یا در X خصوصی شروع کن.');
    } catch (_) {
      output.focus(); output.select();
      status.textContent = say('Select and copy the prepared text manually.', 'متن آماده را خودت انتخاب و کپی کن.');
    }
  });
})();
