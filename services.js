/* Project briefs stay on the visitor's device. */
(() => {
  'use strict';
  const form = document.getElementById('serviceBriefForm');
  if (!form) return;
  const output = document.getElementById('preparedBrief');
  const status = document.getElementById('briefStatus');
  const fa = () => document.documentElement.lang === 'fa';
  const say = (en, persian) => fa() ? persian : en;
  const allowedServices = new Set(['research','localization','video','other']);
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
      input.setCustomValidity(say('Use a public HTTP or HTTPS link.', 'لینک عمومی HTTP یا HTTPS وارد کنید.'));
    }
    if (!form.reportValidity()) return;
    const field = name => form.elements[name].value.trim();
    const selected = form.elements.service.selectedOptions[0].textContent;
    const lines = [say('Romo7 project brief', 'شرح کار برای Romo7'),
      say('Service: ', 'خدمت: ') + selected,
      say('Desired outcome: ', 'خروجی مطلوب: ') + field('question')];
    if (field('input')) lines.push(say('Public input: ', 'ورودی عمومی: ') + field('input'));
    if (field('budget')) lines.push(say('Proposed budget: ', 'بودجهٔ پیشنهادی: ') + field('budget') + ' ' + field('currency'));
    if (field('deadline')) lines.push(say('Desired deadline: ', 'موعد مطلوب: ') + field('deadline'));
    lines.push(say('Please confirm scope, availability and payment terms before starting.', 'لطفاً محدوده، ظرفیت و شرایط پرداخت را قبل از شروع تأیید کنید.'));
    output.value = lines.join('\n\n');
    document.getElementById('briefResult').hidden = false;
    status.textContent = say('Prepared locally; nothing sent. Opening the GitHub request form will also try to copy this brief for you. Paste only non-confidential content, or use Copy brief first.', 'متن فقط روی دستگاه آماده شد و چیزی ارسال نشده است. هنگام بازکردن فرم گیت‌هاب، کپی متن هم امتحان می‌شود؛ فقط اطلاعات غیرمحرمانه را در فرم وارد کنید یا ابتدا دکمهٔ کپی را بزنید.');
    output.focus();
  });
  const publicRequestLink = document.querySelector('#briefResult a[href*="issues/new?template=collaboration.yml"]');
  if (publicRequestLink) {
    // A user click opens GitHub as before. Copy only the already-prepared
    // local text, never auto-submit a public issue or transmit form fields.
    publicRequestLink.addEventListener('click', () => {
      if (!output.value) return;
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        status.textContent = say('Clipboard unavailable: use Copy brief, then paste into GitHub.', 'دسترسی به کلیپ‌بورد ممکن نیست؛ ابتدا متن را کپی و سپس در گیت‌هاب وارد کنید.');
        return;
      }
      navigator.clipboard.writeText(output.value).then(() => {
        status.textContent = say('Brief copied; paste it into the GitHub request form. Nothing was submitted automatically.', 'متن کپی شد؛ آن را در فرم گیت‌هاب وارد کنید. هیچ درخواست خودکاری ارسال نشد.');
      }).catch(() => {
        status.textContent = say('Auto-copy was blocked by the browser; use Copy brief and paste manually.', 'مرورگر کپی خودکار را نپذیرفت؛ از دکمهٔ کپی استفاده کنید و متن را دستی وارد کنید.');
      });
    });
  }
  document.getElementById('copyBrief').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(output.value);
      status.textContent = say('Copied. Open the public GitHub form and paste only non-confidential information; or start privately on X.', 'کپی شد. فرم عمومی گیت‌هاب را باز کنید و فقط متن غیرمحرمانه را وارد کنید؛ یا در X گفت‌وگو را خصوصی آغاز کنید.');
    } catch (_) {
      output.focus(); output.select();
      status.textContent = say('Select and copy the prepared text manually.', 'متن آماده را انتخاب و دستی کپی کنید.');
    }
  });
})();
