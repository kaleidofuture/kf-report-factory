---
title: kf-report-factory
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.44.1
app_file: app.py
pinned: false
---

# KF-ReportFactory

> テンプレートを選んでデータを入力するだけ。定型報告書をPDFで自動生成。

## The Problem

毎週・毎月同じフォーマットの報告書を手作業で作成。コピペミスや書式崩れが頻発。テンプレート化すれば入力だけで済みます。

## How It Works

1. 報告書テンプレートを選択（週次報告、月次報告、売上報告）
2. フォーム入力またはCSVアップロードでデータを投入
3. fpdf2でPDFを自動生成
4. PDFをダウンロード

## Libraries Used

- **Jinja2** — テンプレートエンジン
- **fpdf2** — PDF生成ライブラリ（軽量、依存少）

## Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Hosted on [Hugging Face Spaces](https://huggingface.co/spaces/mitoi/kf-report-factory).

---

Part of the [KaleidoFuture AI-Driven Development Research](https://kaleidofuture.com) — proving that everyday problems can be solved with existing libraries, no AI model required.
