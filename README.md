# SVG → PNG 変換ツール

SVGグラフを選び、DPIを指定してPNG画像に変換する小さなデスクトップアプリです。初期値は300 DPIです。

## 起動方法

Python 3.10以降とTkinterが必要です。macOSではHomebrewのPythonをシステム領域へ直接インストールしようとすると拒否されるため、以下のようにプロジェクト専用の仮想環境を使ってください。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python svg_to_png.py
```



[python3 -m venv .venv-svg
./.venv-svg/bin/python3 -m pip install -r requirements.txt
./.venv-svg/bin/python3 svg_to_png.py]

macOSでCairoSVGの読み込み時にCairoライブラリが見つからないエラーが出た場合は、Homebrewで一度だけ次を実行してください。

```bash
brew install cairo libffi
```

画面でSVGファイル、保存先、DPI（1〜2400）を指定し、「PNGに変換」を押します。SVGがピクセル寸法で保存されていてDPIを変えても出力サイズが変わらない場合は、「出力幅 (px)」に希望する横幅を入力してください。高さは元の縦横比を保って自動計算されます。出力幅を空欄にするとDPI指定で変換します。保存先を選ばずSVGを指定した場合は、元ファイルと同じ場所に同じ名前のPNGを作成します。

## DPIについて

DPIを上げると、SVGのベクター図形をより大きなピクセル寸法で描画します。ファイルサイズと変換に必要なメモリも増えます。SVGに幅・高さが指定されている場合、出力ピクセル数はその物理寸法とDPIから決まります。

## 補足

MatplotlibはSVGを画像として直接読み込む機能を持たないため、このツールではSVGを再描画できるCairoSVGを使っています。これにより、SVGのベクター情報を保ったまま指定DPIでPNG化できます。
