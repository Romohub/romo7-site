/* Project briefs stay on the visitor's device. */
(() => {
  'use strict';
  const form = document.getElementById('serviceBriefForm');
  if (!form) return;
  const output = document.getElementById('preparedBrief');
  const status = document.getElementById('briefStatus');
  const fa = () => document.documentElement.lang === 'fa';
  const say = (en, persian) => fa() ? persian : en;
  document.querySelectorAll('.service-request-link').forEach(link => {
    link.addEventListener('click', () => { form.elements.service.value = link.dataset.service; });
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
    status.textContent = say('Prepared locally. Nothing has been sent. Copy the brief, then open the public GitHub request form or contact Romo7 privately on X.', 'متن روی دستگاه آماده شد؛ چیزی ارسال نشده است. متن را کپی کنید و فرم عمومی گیت‌هاب را باز کنید یا در X تماس خصوصی بگیرید.');
    output.focus();
  });
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
