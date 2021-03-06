# aglab

aglabは自作アナログゲーム(ボードゲーム、カードゲームなど)のテストプレイをするためのフレームワークです。

## 目次

* [aglabは何でないか？](README.md#aglabは何でないか)
* [利用イメージ](README.md#利用イメージ)
* [ディレクトリ構成](README.md#ディレクトリ構成)
* [セットアップ](README.md#セットアップ)
* [使い方](README.md#使い方)
 * [定義ファイル作成](README.md#定義ファイル作成)
 * [Jupyterでの手動テストプレイ](README.md#jupyterでの手動テストプレイ)
 * [Jupyterでの自動テストプレイ](README.md#jupyterでの自動テストプレイ)
* [利用上の注意](README.md#利用上の注意)
* [プロジェクトへの貢献](README.md#プロジェクトへの貢献)
 * [非開発者向け](README.md#非開発者向け)
 * [開発者向け](README.md#開発者向け)


## aglabは何でないか？

1. aglabは自作アナログゲームを「プレイ」するためのフレームワークではありません。  
これは「プレイ体験を向上させる方向での発展は目指していない」ということです。
例えば、画像を表示する等の機能を実装する予定はありません。
むしろ、定義ファイルで手軽にゲームを定義し、CUI(すなわち、キーボード入力だけ)でプレイしたり
プログラムで自動的にテストプレイできることを目指しています。  


## 利用イメージ

以下の流れでaglabを使った自作アナログゲーム開発が行われることを想定して開発しています。  
もちろんこれは一例であり、あなたのゲーム開発フローと異なる場合は使いやすいように使っていただいて構いません。

1. ゲームのアイデアを思いつく。  
2. ゲーム定義ファイルに一通り書き出してみる。  
 * それだけでゲームにとって必要最低限な情報が揃います。  
 終了条件と勝利条件がごっちゃになっている等の“自作ゲームあるある”が防げます。  
 * 必要なコンポーネントの種類、数量が分かります。  
 実際に製品化するのであれば、早い段階でコストの目安が分かるのは良いことです。  
3. aglab上でプレイしてみる。  
 * 足りない定義、ルール等あればどんどん補足します。  
4. パラメータ調整をする。  
 * 自動でテストプレイを実行するツールとその結果を集計・表示するツールを利用して、カードの強さ等のパラメータを
 調整します。(予定)
5. 対人テストプレイ用のマニュアル、コンポーネント一式を用意する。  
 * 簡易マニュアル、必要な情報が記載されただけのカードを出力するツールが作れたらいいなと思っています。(遠い予定)
6. 対人テストプレイの結果をゲーム定義ファイルにフィードバックし、上記手順を繰り返します。
7. aglabの利用はここまで。以後は主に印刷関連の工程になります。

なお、現時点では上記のすべてが実現可能というわけではなく、「〜できる(ようにしたい)」といった意味合いで捉えてください。


## ディレクトリ構成

```
/definition :ゲーム定義ファイル
/doc        :ドキュメント
/module     :共通、再利用可能なゲーム定義のモジュール
/src        :aglabのソースコード
/test       :aglabのテストコード
/tool       :aglabを活用するためのツール
```


## セットアップ

aglabを実行するためには、Python2.7 および NumPy, pandas 等のライブラリが必要です。
また、Jupyterを利用すれば手軽にテストプレイを開始することができます。  

それぞれを個別にインストールすることもできますが、[Anaconda](https://docs.continuum.io/anaconda/install)
をインストールするのが近道です。  
開発はAnacondaをインストールしたMacOS上で行われています。  

上記がインストールされた環境にて以下のコマンドを実行し、aglabを取得します。
```
git clone git@github.com:fullkawa/aglab.git
```


## 使い方

### 定義ファイル作成

* definition/mygame.py を直接編集するか、コピーしてお使いください。
* テンプレート(mygame.py)に定義されている属性(title等)はすべて必須です。  
#でコメントアウトされている属性は任意で設定してください。
* 各属性の説明は、定義ファイル内コメントおよび[デザイナーズガイド](https://github.com/fullkawa/aglab/blob/master/doc/designersguide.md)を参照してください。


### Jupyterでの手動テストプレイ

1. Anacondaのランチャーからnotebook(Jupyter Notebook)を起動します。
2. aglab/testplay.ipynbを開きます。
3. 一番上のセルから順に実行します。メニューから"Cell > Run All"を選択しても良いでしょう。
4. ゲームのプレイについては"How to play"を参照してください。


### Jupyterでの自動テストプレイ

1. Anacondaのランチャーからnotebook(Jupyter Notebook)を起動します。
2. aglab/testauto.ipynbを開きます。
3. 一番上のセルから順に実行します。メニューから"Cell > Run All"を選択しても良いでしょう。


## 利用上の注意

* aglabはまだ開発の初期段階にあります。定義ファイルの記述方式が大幅に変わる可能性もありますので、  
ご了承願います。
* ゲームの「ルール」は著作権の保護対象にならないという話もありますが、当方では何の保証もいたしません。  
ゲーム定義ファイルの共有・公開については十分ご注意ください。  


## プロジェクトへの貢献

### 非開発者向け

非開発者であってもプロジェクトへの貢献は可能です。  
本READMEファイルなどのドキュメントを英訳していただける方の協力は大歓迎です。


### 開発者向け

不具合報告や追加機能の要望を[Issues](https://github.com/fullkawa/aglab/issues)から登録していただくのも
貢献の一つの形ですが、あなたが開発者であるなら実際に不具合を修正あるいは追加機能を実装してPull Requestを送って
いただくほうがより助かります。  

