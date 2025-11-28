# agentUniverse
****************************************
言語バージョン: [英語](./README.md) | [中国語](./README_zh.md) | [日本語](./README_jp.md)

![](https://img.shields.io/badge/framework-agentUniverse-pink)
![](https://img.shields.io/badge/python-3.10%2B-blue?logo=Python)
[![](https://img.shields.io/badge/%20license-Apache--2.0-yellow)](LICENSE)
[![Static Badge](https://img.shields.io/badge/pypi-v0.0.19-blue?logo=pypi)](https://pypi.org/project/agentUniverse/)

![](docs/guidebook/_picture/logo_bar.jpg)
****************************************

## agentUniverseとは何ですか？

**agentUniverseは、大型言語モデルに基づくマルチエージェントフレームワークです。** agentUniverseは、柔軟で拡張性のある単一エージェント構築能力を提供します。agentUniverseのコアには、多様なマルチエージェント協調モデルコンポーネントが豊富に揃っており（協調モデル工場として考えることができます）、エージェントがそれぞれの役割を果たしながら、異なる分野の問題を解決する際に最大の能力を発揮できるようにします。また、agentUniverseは分野の経験の融合に注力し、容易にその経験をエージェントの業務に取り入れる手助けをします。🎉🎉🎉

**🌈🌈🌈agentUniverseは、開発者や企業が専門家レベルの強力なエージェントを簡単に構築し、協力して働くことを支援します。**

![](docs/guidebook/_picture/agent_universe_framework_resize.jpg)

フレームワークには、実際のビジネスシナリオで効果が証明されたいくつかのプリインストールされたマルチエージェントコラボレーションパターンが含まれており、今後も豊富になる予定です。現在リリース予定のパターンには以下が含まれます：

PEERパターン： このパターンは、Plan（計画）、Execute（実行）、Express（表現）、Review（レビュー）の4つの異なるエージェントの役割を利用して、複雑なタスクを多段階に分解し、順次実行します。また、評価フィードバックに基づいて自律的な反復を行い、推論および分析タスクのパフォーマンスを向上させます。

DOEパターン： このパターンは、Data-fining（データ精製）、Opinion-inject（意見注入）、Express（表現）の3つのエージェントで構成され、データ集約型および高計算精度のタスクを解決し、事前に収集および構造化された専門家の意見と組み合わせることで、最終結果を生成します。

これからもっと多くのパターンが登場します...

****************************************

## 目録
* [クイックスタート](#クイックスタート)  
* [インテリジェントエージェントアプリケーションの構築方法](#インテリジェントエージェントアプリケーションの構築方法)
* [キャンバス式開発プラットフォームの構築](#キャンバス式開発プラットフォームの構築)
* [なぜエージェントユニバースを使用するのか](#なぜエージェントユニバースを使用するのか)  
* [サンプルアプリ](#サンプルアプリ)  
* [文書資料](#文書資料)  
* [サポート](#サポート)

****************************************

## クイックスタート
### クイックインストール
pipを使用：
```shell
pip install agentUniverse
```

### 最初のチュートリアルケースを実行する

あなたの最初のケースを実行することで、チュートリアルを通じてagentUniverseによって構築されたエージェント（グループ）の動作をすぐに体験できます。

詳細な手順については、ドキュメントを参照してください: [最初のチュートリアルケースを実行する](docs/guidebook/en/Get_Start/2.Run_Your_First_Tutorial_Example.md) 。

****************************************

## インテリジェントエージェントアプリケーションの構築方法

### agentUniverseサンプルプロジェクト
⌨️ agentUniverseサンプルプロジェクト: [agentUniverse Standard Project](examples/sample_standard_app)

#### 単体知能エージェントの迅速構築
[単体のインテリジェントエージェントを迅速に構築する](docs/guidebook/en/Get_Start/3.Quick_Guide_to_Build_Single_Agent.md)の章を読むことで、単一のインテリジェントエージェントを迅速に構築する方法を理解し、ツール、知識ベース、RAG技術などの能力を活用してインテリジェントエージェントの能力を強化する方法を習得できます。また、インテリジェントエージェントの設定、テスト、調整、サービス化、効果評価など、一連の基本的なインテリジェントエージェントアプリケーションの開発プロセスも学ぶことができます。

#### 典型的なマルチエージェントアプリケーションの構築
複雑なタスクシナリオにおいて、エージェントの能力を複数のエージェントに分割し、協力してタスクのパフォーマンスを向上させる方法については、[典型的なマルチエージェントアプリケーションの構築](docs/guidebook/en/Get_Start/4.Building_Typical_Multi-Agent_App.md)章を通じてさらに学ぶことができます。

#### 智能体テンプレートの構築と使用
効果的なエージェントのパターンをテンプレートとして確立し、使用する方法については、[エージェントテンプレートの構築と使用](docs/guidebook/en/Get_Start/5.Creating_and_Using_Agent_Templates.md)の章をご覧ください。これにより、今後のエージェントの構築効率が大幅に向上し、共有が容易になります。

#### MCP サービスの利用と公開
agentUniverse フレームワークでMCPサービスを迅速に利用または公開する方法は、以下のドキュメントを参照してください： [MCPサーバーの利用方法](docs/guidebook/en/How-to/Use%20and%20Publish%20MCP%20Server/How_to_Use_MCP_Servers.md) 、 [MCPサーバーの公開方法](docs/guidebook/en/How-to/Use%20and%20Publish%20MCP%20Server/How_to_Publish_MCP_Servers.md).

#### よく使われる利用技術
[一般的な使用のコツ](docs/guidebook/en/Get_Start)セクションを通じて、スマートエージェントアプリケーションの構築プロセスにおける一般的なテクニックを理解できます。たとえば、スマートエージェントプロセスにメモリモジュールを組み込む方法や、プロジェクト内のプロンプトを効率的に管理する方法などです。

### キャンバス式開発プラットフォームの構築

agentUniverseは、ローカルベースのキャンバス型開発プラットフォーム機能を提供しています。以下の手順に従って、迅速に起動してください。

**pipを使用**
```shell
pip install magent-ui ruamel.yaml
```

**一鍵で実行する**

sample_apps/workflow_agent_app/bootstrap/platformの下にある[product_application.py](examples/sample_apps/workflow_agent_app/bootstrap/platform/product_application.py)ファイルを実行して、一括起動します。

詳細については、[製品化プラットフォームの迅速な開始](./docs/guidebook/en/How-to/Guide to Visual Agentic Workflow Platform/Product_Platform_Quick_Start.md) と [製品化プラットフォームの進階ガイド](./docs/guidebook/en/How-to/Guide to Visual Agentic Workflow Platform/Product_Platform_Advancement_Guide.md) をご覧ください。本機能は 🔗[difizen](https://github.com/difizen/magent) プロジェクトチームと X agentUniverse プロジェクトチームが共同で提供しています。

****************************************

## なぜエージェントユニバースを使用するのか
### 設計の思考

![](docs/guidebook/_picture/agentuniverse_structure.png)

agentUniverseのコアは、単一のエージェントを構築するためのすべての重要なコンポーネント、マルチエージェント間の協力メカニズム、および専門家の経験を注入するメカニズムを提供し、開発者が専門的なノウハウを持つスマートアプリケーションを簡単に構築できるようにします。

### 多エージェント協調メカニズム

agentUniverseは、実際の産業で検証された有効なマルチエージェント協力モデルのコンポーネントをいくつか提供しており、その中で「PEER」は最も特徴的なモデルの一つです。

PEERパターン： このパターンは、Plan（計画）、Execute（実行）、Express（表現）、Review（レビュー）の4つの異なるエージェントの役割を利用して、複雑なタスクを多段階に分解し、順次実行します。また、評価フィードバックに基づいて自律的な反復を行い、推論および分析タスクのパフォーマンスを向上させます。

PEERモードはエキサイティングな結果を得ることができ、最新の研究成果や実験結果については以下の文献で読むことができます。

### いんよう

BibTeX formatted
```text
@misc{wang2024peerexpertizingdomainspecifictasks,
      title={PEER: Expertizing Domain-Specific Tasks with a Multi-Agent Framework and Tuning Methods}, 
      author={Yiying Wang and Xiaojing Li and Binzhu Wang and Yueyang Zhou and Han Ji and Hong Chen and Jinshi Zhang and Fei Yu and Zewei Zhao and Song Jin and Renji Gong and Wanqing Xu},
      year={2024},
      eprint={2407.06985},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2407.06985}, 
}
```
文献の紹介：この文献では、PEER多エージェントフレームワークのメカニズム原理について詳しく説明するとともに、実験部分では**完全性、関連性、簡潔性、事実性、論理性、構造性、包括性の7つの次元で評価（各次元の満点は5点）**を行っています。PEERモデルは各評価次元の平均スコアがBabyAGIを上回り、完全性、関連性、論理性、構造性、包括性の5つの次元で顕著な優位性を持っています。また、PEERモデルはGPT-3.5 turbo (16k)モードでBabyAGIに対して選抜勝率が83%に達し、GPT-4oモデルでは選抜勝率が81%に達しています。詳細については文献をご覧ください。

🔗https://arxiv.org/pdf/2407.06985

### コア特性
agentUniverseの主な特徴を以下のようにまとめました：

柔軟で拡張可能なエージェント構築能力： エージェント構築に必要なすべての重要コンポーネントを提供し、すべてのコンポーネントはユーザーが独自のエージェントを強化するためにカスタマイズをサポートします。

豊富で効果的なマルチエージェント協調モード： PEER（Plan/Execute/Express/Review）、DOE（Data-fining/Opinion-inject/Express）など、産業で検証された協調モードを提供し、ユーザーが新しいモードを自分で編成できるようにサポートし、複数のエージェントが有機的に協力できるようにします。

分野の経験を簡単に取り入れる： 分野に特化したプロンプト、知識の構築と管理能力を提供し、分野レベルのSOPを編成・注入することをサポートし、エージェントを分野の専門家レベルに合わせることができます。

💡 更なる特徴については、[agentUniverseの核心特性](docs/guidebook/en/Concepts/Core_Features.md)の部分を参照してください。

****************************************

## サンプルアプリ
🚩 [法律相談Agent_V2](docs/guidebook/en/Examples/Legal_Advice.md)

🚩 [Pythonコード生成と実行Agent](docs/guidebook/en/Examples/Python_Auto_Runner.md)

🚩 [多回多Agentによるディスカッショングループ](docs/guidebook/en/Examples/Discussion_Group.md)

🚩 [PEERマルチAgentモードに基づいた金融イベント分析](docs/guidebook/en/Examples/Financial_Event_Analysis.md)

🚩 [反射的ワークフロー翻訳エージェントの複製](docs/guidebook/en/Examples/Translation_Assistant.md)

****************************************

## 文書資料

### ユーザーガイドマニュアル
💡 詳細な情報については、[ユーザーガイド](./docs/guidebook/en/Contents.md)を参照してください。

### APIリファレンス
💡 [APIリファレンス](https://agentuniverse.readthedocs.io/en/latest/)を参照して、技術的な詳細をご確認ください。

****************************************

## サポート
### お問い合わせ
😊 Email: 
* [jihan.hanji@antgroup.com](mailto:jihan.hanji@antgroup.com)
* [jerry.zzw@antgroup.com](mailto:jerry.zzw@antgroup.com)
* [jinshi.zjs@antgroup.com](mailto:jinshi.zjs@antgroup.com)

### twitter
ID: [@agentuniverse_](https://x.com/agentuniverse_)
