# temporal-test

Temporal の Python SDK を使った最小サンプルです。**Signal / Query** の動きを実際に手で叩いて確認できる構成になっています。

## このサンプルでわかること

- Workflow を起動して長時間生かしておく方法
- 外部から **Signal** を送って Workflow の内部状態を更新する方法
- 外部から **Query** を投げて Workflow の現在の状態を取り出す方法
- Workflow から Activity を呼び出す基本パターン

## シナリオ

`GreetingWorkflow` は名前を受け取って "Hello, {name}!" という挨拶文を作るワークフローです。

- `submit_name(name)` **Signal** で名前を投入すると、Activity が走って挨拶文が生成される
- `get_pending` / `get_greetings` **Query** で「未処理の名前」「これまで作った挨拶のリスト」をいつでも覗ける
- `exit` **Signal** を送るとワークフローが完了し、最終的な挨拶リストを返す

## 必要なもの

- Python 3.9 以上
- ローカルで動作する Temporal Server (`localhost:7233`)
  - 一番ラクなのは [Temporal CLI](https://docs.temporal.io/cli) を使う方法
    ```bash
    temporal server start-dev
    ```
  - Docker Compose を使いたい場合は [temporalio/docker-compose](https://github.com/temporalio/docker-compose) を参照

Web UI はデフォルトで http://localhost:8233 (CLI dev server) もしくは http://localhost:8080 (docker-compose) です。

## セットアップ

```bash
# 仮想環境を作る (任意)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存をインストール
pip install -r requirements.txt
```

## 動かしかた

ターミナルを **2つ以上** 開いて操作します。

### 1. Worker を起動 (Terminal A)

```bash
python run_worker.py
```

`Worker started on task queue: greeting-task-queue` と出れば OK。このプロセスは起動したままにします。

### 2. Workflow を起動 (Terminal B)

```bash
python start_workflow.py
```

`Started workflow: id=greeting-workflow, ...` と表示されたら、Workflow は走り続けたまま Signal を待っている状態になります。

Web UI の Workflows 一覧から `greeting-workflow` が **Running** で見えるはずです。

### 3. Signal を送る (Terminal B)

```bash
python send_signal.py Alice
python send_signal.py Bob
python send_signal.py Carol
```

Worker 側のログに `Composing greeting for Alice` のように Activity が動いた跡が出ます。

### 4. Query で状態を確認 (Terminal B)

```bash
python send_query.py greetings   # これまで作られた挨拶文のリスト
python send_query.py pending     # まだ処理待ちの名前 (基本は空のはず)
```

Workflow を止めずに、現在の内部状態をいつでも取得できることに注目してください。これが Query の魅力です。

### 5. Workflow を終了

```bash
python send_signal.py exit
```

Workflow が完了し、戻り値として挨拶リストが返ります。Web UI で **Completed** になっていることを確認できます。

## ファイル構成

| ファイル | 役割 |
| --- | --- |
| `workflows.py` | `GreetingWorkflow` 定義 (Signal / Query / Activity 呼び出し) |
| `activities.py` | `compose_greeting` Activity |
| `run_worker.py` | Worker プロセス (Workflow と Activity を実行する側) |
| `start_workflow.py` | Workflow を新規に起動するクライアント |
| `send_signal.py` | 起動中の Workflow に Signal を送るクライアント |
| `send_query.py` | 起動中の Workflow に Query を投げるクライアント |
| `pyproject.toml` / `requirements.txt` | 依存関係 (`temporalio`) |

## ポイント解説

### Signal は「外からの状態変化トリガー」

```python
@workflow.signal
def submit_name(self, name: str) -> None:
    self._pending_names.append(name)
```

`@workflow.signal` を付けたメソッドは外部から呼べます。中で `await` せずに、状態を変えるだけにするのが基本パターン。実処理は `run` 側で `wait_condition` で拾います。

### Query は「副作用なしの状態取得」

```python
@workflow.query
def get_greetings(self) -> list[str]:
    return list(self._greetings)
```

Query ハンドラの中で Activity を呼んだり、状態を書き換えたりしてはいけません。**読み取り専用** が鉄則です。

### Workflow は決定的実行が必須

`workflows.py` 内では時刻取得・ランダム値・直接の I/O などをしてはいけません (再生が壊れます)。そういう処理は全部 Activity 側 (`activities.py`) に逃がします。

## トラブルシュート

- **`ConnectionRefusedError`** … Temporal Server が起動していない。`temporal server start-dev` を確認。
- **Worker のログに何も出ない** … Signal を送る前に Worker と Workflow の両方が起動済みか確認。
- **`WorkflowAlreadyStarted`** … 前回の `greeting-workflow` がまだ動いている。`send_signal.py exit` で終わらせるか、Web UI から Terminate してから再起動。
