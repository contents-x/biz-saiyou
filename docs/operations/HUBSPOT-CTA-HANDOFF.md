# HUBSPOT-CTA-HANDOFF — お問い合わせのHubSpot連携仕様

> イチ推し採用のお問い合わせフォームを、既存の姉妹サイト（Contents X / BizManga）と同じHubSpotアカウントに送信する実装仕様。**実IDは非公開**（[INFRA-PRIVATE.md](INFRA-PRIVATE.md) 参照）。

## TL;DR

HubSpot Forms API v3 のサブミットエンドポイントに、`fetch()` で直接POSTする。埋め込みウィジェット不使用。サイトHTML/CSSは自前、送信処理だけAPIを叩く。

## 接続情報（実値は非公開）

| 項目 | 値 |
|---|---|
| Portal ID | `<INFRA-PRIVATE.md 参照>` |
| Form GUID | `<INFRA-PRIVATE.md 参照>`（既存の共通フォームを再利用） |
| エンドポイント | `https://api.hsforms.com/submissions/v3/integration/submit/{PORTAL_ID}/{FORM_GUID}` |
| メソッド | POST / Content-Type: application/json |
| CORS | 公開サブミット用なので別ドメイン可（設定不要） |
| 識別 | `SERVICE_NAME = "イチ推し採用"`（2026-10-31〜。それ以前は「ビズ採用」、その前は「リクルートX」）＋ `context.pageName` でHubSpot側がフィルタ可 |

**完全に別フォームに分けたい時のみ**、HubSpot側で新規フォーム作成が必要（その際は Form GUID を新IDに置換）。

## フィールドマッピング（厳守・既存プロパティ名）

| 画面入力 | HubSpot内部name | 備考 |
|---|---|---|
| 会社名 | `company` | |
| 部署 | `busyo` | カスタムプロパティ。`department` でなく `busyo`（ローマ字）が正。**HubSpot 側で必須**（未送信も空文字も 400 `REQUIRED_FIELD` で拒否。2026-09-29 本番で確認）→ 画面でも必須にしている |
| お名前 | `lastname` と `firstname` 両方に同じフルネーム | 画面1項目→HubSpot側は姓名2プロパティ |
| メール | `email` | |
| お問い合わせ内容 | `message` | 末尾に送信元トラッキング情報を付加 |

## 参照HTML

```html
<form id="rx-contact-form" class="rx-form" novalidate>
  <label class="rx-form__field">
    <span class="rx-form__label">会社名 <em>必須</em></span>
    <input type="text" name="company" required autocomplete="organization">
  </label>
  <label class="rx-form__field">
    <span class="rx-form__label">部署 <em>必須</em></span>
    <input type="text" name="department" required autocomplete="organization-title">
  </label>
  <label class="rx-form__field">
    <span class="rx-form__label">お名前 <em>必須</em></span>
    <input type="text" name="fullName" required autocomplete="name">
  </label>
  <label class="rx-form__field">
    <span class="rx-form__label">メールアドレス <em>必須</em></span>
    <input type="email" name="email" required autocomplete="email">
  </label>
  <label class="rx-form__field">
    <span class="rx-form__label">お問い合わせ内容 <em>必須</em></span>
    <textarea name="message" rows="6" required></textarea>
  </label>
  <button type="submit" class="rx-form__submit">送信する</button>
</form>
```

## 参照JS（安全なDOM操作で実装）

```js
(function () {
  // 実IDは INFRA-PRIVATE.md / 公開リポでは下記は ENV や非公開設定から注入する想定
  var HUBSPOT_PORTAL_ID = '<REDACTED>';
  var HUBSPOT_FORM_GUID = '<REDACTED>';
  var SERVICE_NAME      = 'イチ推し採用';

  var form = document.getElementById('rx-contact-form');
  if (!form) return;
  var PARAMS = new URLSearchParams(window.location.search);

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var submitBtn = form.querySelector('.rx-form__submit');
    submitBtn.disabled = true;
    submitBtn.classList.add('is-sending');

    var fd = new FormData(form);
    var fullName = String(fd.get('fullName') || '');

    // 送信元トラッキングをmessage末尾に追記
    var tracking = ['[' + SERVICE_NAME + '経由のお問い合わせ]'];
    var utmSource   = PARAMS.get('utm_source');
    var utmMedium   = PARAMS.get('utm_medium');
    var utmCampaign = PARAMS.get('utm_campaign');
    var source      = PARAMS.get('source');
    if (utmSource)   tracking.push('流入元: ' + utmSource);
    if (utmMedium)   tracking.push('媒体: ' + utmMedium);
    if (utmCampaign) tracking.push('キャンペーン: ' + utmCampaign);
    if (source)      tracking.push('参照ページ: ' + source);
    tracking.push('ページ: ' + window.location.href);
    var trackingNote = '\n\n---\n' + tracking.join('\n');

    var payload = {
      fields: [
        { name: 'company',   value: String(fd.get('company')    || '') },
        { name: 'busyo',     value: String(fd.get('department') || '') },
        { name: 'lastname',  value: fullName },
        { name: 'firstname', value: fullName },
        { name: 'email',     value: String(fd.get('email')      || '') },
        { name: 'message',   value: String(fd.get('message')    || '') + trackingNote }
      ],
      context: {
        pageUri:  window.location.href,
        pageName: SERVICE_NAME + ' - お問い合わせ'
      }
    };

    fetch('https://api.hsforms.com/submissions/v3/integration/submit/'
        + HUBSPOT_PORTAL_ID + '/' + HUBSPOT_FORM_GUID, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (res.ok) return res.json();
        return res.text().then(function (t) { throw new Error(t); });
      })
      .then(function () {
        // 成功表示は createElement + textContent で安全に組み立て（XSS対策）
        var thanks = document.createElement('div');
        thanks.className = 'rx-form__thanks';
        var h = document.createElement('p');
        h.className = 'rx-form__thanks-h';
        h.textContent = 'お問い合わせありがとうございます。';
        var s = document.createElement('p');
        s.className = 'rx-form__thanks-s';
        s.textContent = '3営業日以内にご連絡いたします。';
        thanks.appendChild(h);
        thanks.appendChild(s);
        form.parentNode.insertBefore(thanks, form.nextSibling);
        form.style.display = 'none';
      })
      .catch(function (err) {
        console.error('HubSpot submission error:', err);
        submitBtn.disabled = false;
        submitBtn.classList.remove('is-sending');
        alert('送信に失敗しました。お手数ですが、もう一度お試しください。');
      });
  });
})();
```

**実装時の補足**: 現在の `js/main.js` には HubSpot IDがハードコードされている（フロントエンドからの直接POST方式のため、ブラウザのview-sourceでは見える）。これは仕様であり、完全秘匿したい場合はサーバーサイドproxy経由に構成変更が必要。

## セキュリティ強化（実装済み・2026-06-10）

- **honeypot**: 不可視フィールド `website`（offscreen配置）。botが埋めたら送信せず成功表示だけ出す
- **入力上限**: company 200 / busyo 100 / fullName 100 / email 254 / message 4000（HTML `maxlength` + JS側でも `slice`）
- **入力trim + email形式チェック**: 送信前にJSで検証、エラーは `role="alert"` のインライン表示（alertダイアログ廃止）
- **URLパラメータ制限**: UTM等は80字、pageURLは300字に切り詰めてからトラッキング情報に使用
- **CSP**: 両ページの `<meta http-equiv="Content-Security-Policy">` で `connect-src` を `'self' https://api.hsforms.com` に限定。**GA4/Clarity追加時はCSPの追記が必須**

## 実装時の判断ポイント

- **送信元の識別必須**: `SERVICE_NAME` と `context.pageName` に必ずサービス名（現在「イチ推し採用」）を入れる（既存2サイトとの識別）。サービス名を変えると HubSpot 上の識別文字列も変わるので、HubSpot 側で旧名で絞り込んでいるビュー・ワークフローがあれば合わせて直す
- **Google広告CV計測**: 既存サイトのCV IDはイチ推し採用用ではない → そのままコピー禁止
- **HubSpotトラッキングスクリプト**（任意）: 既存BizMangaは「初操作 or 4秒後に遅延ロード」で最適化済み。送信自体はAPI直叩きなので無くても動く
- **HTML/CSS/JS分離**: 送信処理は外部JSに分ける（プロジェクト規約・[CLAUDE.md](../../CLAUDE.md)）
- **innerHTML 禁止**: 成功表示は `createElement` + `textContent` で組み立てる（セキュリティフック警告対象）

## 完了後にやること

1. 1件テスト送信し、HubSpot該当フォームの送信履歴に「[イチ推し採用経由のお問い合わせ]」付きで記録されるか確認
2. [SPEC.md](../specs/SPEC.md) / [INFRA.md](INFRA.md) に「お問い合わせ＝HubSpot（IDは INFRA-PRIVATE.md）に送信」と追記

## ユーザーに確認するべきこと

お問い合わせ通知の宛先メールは、**既存フォーム再利用の場合、通知先も既存と同じ**になる。イチ推し採用専用通知先に分けたい場合は、HubSpot側でフォーム分割 or ワークフロー条件分岐の設定が別途必要。
