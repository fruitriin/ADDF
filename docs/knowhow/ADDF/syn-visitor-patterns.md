---
title: syn::Visit で AST から情報を集めるパターン
created: 2026-06-11
last_verified: 2026-06-11
depends_on: []
status: active
---

# syn::Visit で AST から情報を集めるパターン

> 出典: MagiaMagica (コード可視化ツール) Phase 1.2 で確立、Phase 1.3 (再帰展開)・1.4 (call site 抽出)・3.4 (近似データフロー)・4.0 (impl メソッド索引) で拡張

Rust ソースを syn でパースし、AST から構造情報を抽出する種類のツール (可視化・解析・lint 等) の定型と落とし穴。

## 基本形: 単一関心の Visitor を関数スコープに閉じ込める

```rust
fn count_await_points(item_fn: &ItemFn) -> u32 {
    struct Counter { count: u32 }
    impl<'ast> Visit<'ast> for Counter {
        fn visit_expr_await(&mut self, node: &'ast syn::ExprAwait) {
            self.count += 1;
            syn::visit::visit_expr_await(self, node);  // 必ず再帰
        }
    }
    let mut counter = Counter { count: 0 };
    counter.visit_block(&item_fn.block);
    counter.count
}
```

ポイント:

- 1関心1 visitor。`Counter`, `TryFinder`, `UnsafeFinder` のように単機能に絞る
- 関数内に閉じ込めれば `pub` 露出ゼロ (POSD「情報隠蔽」)
- **再帰呼び出しを忘れない**: `syn::visit::visit_*` を呼ばないとサブツリーが走査されない。バグの定番

## 同じ AST を2回走査しそうになったら集約せよ

NG パターン:
```rust
let kind = classify_statement(stmt);   // visitor 1
let early_return = is_early_return(stmt);  // visitor 2 (同じツリーをまた走る)
let has_unsafe = statement_contains_unsafe(stmt);  // visitor 3
```

GOOD パターン:
```rust
struct StatementScan { kind: OperationKind, early_return: bool, has_unsafe: bool }

fn scan_statement(stmt: &Stmt) -> StatementScan {
    let is_return_stmt = matches!(stmt, Stmt::Expr(Expr::Return(_), _));
    let mut visitor = StatementVisitor::default();
    visitor.visit_stmt(stmt);
    StatementScan { /* 1回のスキャンで全部出す */ }
}
```

最初は3〜4機能でも分かれていられるが、`if` / `match` 対応が増えると visitor の本数が指数的に増えうる。**N 個の関心事を 1 visitor に統合する**設計に最初から寄せる。

## list/parse の API 規約: 探索範囲を揃える

`list_functions` (名前列挙) と `parse_function` (実体取得) で別々の visitor を使う場合、両者の再帰方針 (`mod` 内に降りるか / `impl` 内に降りるか) を**明示的に揃える**。揃わないと「list には載るが parse できない名前」が出て API として矛盾する。

規約をコードコメントとテストで残す:
```rust
/// 規約: list_functions が返す任意の名前は parse_function で必ず発見できる
```
```rust
#[test]
fn listed_names_are_all_parseable() {
    for name in list_functions(src).unwrap() {
        parse_function(src, name).unwrap();
    }
}
```

これは POSD「複雑性を下に押し下げる」の好例。利用者が「あ、これは mod 内だから別 API を使わないと」と分岐する形は避ける。

## ID 採番は `Allocator` パターンに閉じ込める

```rust
pub(crate) struct NodeIdAllocator { next: u32 }
impl NodeIdAllocator {
    pub(crate) fn allocate(&mut self) -> NodeId {
        let id = NodeId(self.next);
        self.next += 1;
        id
    }
}
```

- IR 側で `pub struct NodeId(pub u32)` と公開していても、採番はアロケータでのみ行う規約にすると単調増加・一意性が守れる
- 乱数を使わないので決定論的 (出力の決定論性を仕様要件に持つツールへの布石)

## lifetime の落とし穴: `'src` と `'ast` を混ぜない

```rust
struct FunctionRefCollector<'src> {
    target: String,
    found: Option<&'src ItemFn>,
}
impl<'ast> Visit<'ast> for FunctionRefCollector<'ast> { /* ... */ }
```

`'src` と `'ast` は事実上同じ lifetime に単一化されるが、命名が分かれていると読者が「別物」と誤読する。**Visit の対象になる struct の lifetime は `'ast` で統一する** ことで読みやすくなる。

## thiserror + 候補提示

```rust
#[derive(Debug, Error)]
pub enum Error {
    #[error("Rust 構文エラー: {0}")]
    Syntax(#[from] syn::Error),

    #[error(
        "関数 `{name}` が見つかりません (候補: {})",
        if candidates.is_empty() { "なし".to_string() } else { candidates.join(", ") }
    )]
    FunctionNotFound { name: String, candidates: Vec<String> },
}
```

- `#[error(..., expr)]` で条件分岐を埋め込める
- `#[from] syn::Error` で `?` 演算子経由の伝播が無痛
- ユーザー向けのエラーは**候補を載せる**だけで体感が大きく変わる (POSD: 「エラーから学べる」)

## 再帰構造の展開: 子ノード切り出しビルダパターン

制御構造 (`if` / `match` / ループ) をネスト構造ごと別ノード (出典では AuxRing) に切り出すときの定型。

```rust
struct NodeBuilder<'a> {
    allocator: &'a mut NodeIdAllocator,
    ctx: ParseContext,        // fn_is_unsafe 等を1構造体に集約 (引数膨張の防止)
    nodes: Vec<Node>,         // 再帰中に子から push される
    edges: Vec<Edge>,
}

fn build_node(&mut self, kind, stmts, role, span) -> NodeId {
    let id = self.allocator.allocate();  // 親 ID を先に採番 (子の Edge.source に必要)
    for stmt in stmts { /* 制御構造なら spawn_child で再帰 */ }
    self.nodes.push(/* 親自身は最後に push */);
    id
}
```

ポイント:

- **親 ID 先採番 → 子 push → 親 push → 最後に ID 順 sort**。再帰中の push 順は
  「子が先」になるため、`sort_by_key(|n| n.id)` で「ソース出現順の深さ優先」を回復する。
  ID 採番が決定論的ならソート結果も決定論的
- **非ブロックの式体は statement 化して経路を一本化する**: match のアーム体 `1 => a()` は
  `Stmt::Expr(expr.clone(), None)` に包んで同じ `build_node` に流す。
  これで `_ => match ...` のような入れ子も特別扱いなしで再帰展開される (初期フェーズでは clone は許容)
- **二重計上の防止**: 制御構造を親ノード側の Operation (Branch/Match/Loop) にするとき、
  scan するのは条件式・被検査式・イテレータ式のみ。本体ブロックは子ノード側が処理するため、
  本体まで scan すると `unsafe` / `?` のフラグが親子で二重計上される
- `clippy::too_many_arguments` 対策: 役割構造体 (anchor/ordinal/label をまとめた struct) を
  呼び出し側で組み立てて渡す (バラで渡さない)
- **インデックス系の `u32::try_from(..).unwrap_or(u32::MAX)` は禁じ手** (レビュー指摘の定番):
  後続フェーズが「存在しない位置」を有効値として参照する無音バグになる。実用上起こらない
  超過なら `expect` で明示的に落とす。センチネルで誤魔化さない (POSD「エラーを存在しないものとして定義」)

## call site 抽出と近似パス解決

意味解決なし (構文情報のみ) で call site を拾うときの定型と落とし穴。

- **`visit_macro` は `Stmt::Macro` と `Expr::Macro` の両方を1フックで捕捉する**。
  `visit_expr_macro` だけだと statement 位置のマクロ (`println!("x");`) を取り逃がす。
  マクロ呼び出しを拾うなら `visit_macro` 一択
- **マクロのトークン列内部は走査されない**: `println!("{}", foo())` の `foo()` は
  syn の visitor が式として降りないため call 抽出から漏れる。マクロは名前ベースの
  白リスト判定 (展開しない) が初期フェーズの割り切り
- **パス前方一致はセグメント境界つきにする**: `path.strip_prefix(prefix)` 後に
  `rest.is_empty() || rest.starts_with("::")` を要求。素の `starts_with` だと
  `std::io` が `std::iox::fake` に誤一致する
- **use 文の機械的展開 (UseMap)**: `UseTree` の Path/Name/Rename/Group を再帰 walk、
  Glob は無視。先頭セグメント名 → フルパスの HashMap を作り、call パスの先頭だけ
  置換する。モジュール境界は無視 (同名 use は後勝ち) で近似解析には十分
- **メソッド呼び出しはレシーバ型が分からない**ため解決不能。`.method` 形式で保持して
  既定の効果分類に倒す (意味解決が必要になったら ra_ap_hir 等の導入で再訪)

## クレート選定メモ

- `syn = { version = "2", features = ["full", "visit", "extra-traits"] }`: `full` を入れないと `ItemFn::block` などが取れない
- `proc-macro2 = { version = "1", features = ["span-locations"] }`: feature を入れないと `span.start().line` が取れない
- `quote = "1"`: `ToTokens::to_token_stream().to_string()` でシグネチャを文字列化 (`syn::Signature` には `to_string()` が無い)
- `thiserror = "2"`: 現行 stable に追従。`#[from]` / `#[error(..)]` の挙動は v1 と互換

## 近似データフロー解析

意味解決なしの syn ベース def/use 抽出の定型:

- **候補抽出 (純粋構文) とスコープ解決 (状態機械) を分離する**: 識別子の出現は
  単一セグメント・型引数なしのパスを全部候補として集め、let / 引数 / パターン束縛で
  積んだスコープ (`Vec<BTreeMap>` フレームの push/pop) で解決できたものだけ採用する。
  関数名・unit variant・定数はスコープに無いため**自然に落ち**、大文字小文字
  ヒューリスティクスを最小化できる (パターン側の unit variant 曖昧性のみ
  先頭大文字で除外)
- **スコープ追跡は既存の再帰構築 (上記ビルダ) と並走させる**: 別パスで AST を
  二重走査すると Operation 添字との対応付けが分岐しやすい。フレーム push は
  ビルダ再帰の冒頭、pop はノード確定 (push) 直後。本体に Operation を持たない
  束縛 (引数・for パターン・match アーム・if let) は `seeds` 引数で冒頭にまとめて def
- **解決順序が要**: `let x = x + 1` は uses 解決 → reassign/define の順に処理しないと
  シャドーイングが壊れる
- **再代入 = 再定義の実装**: 変数が見えるフレームの位置はそのまま、レコードだけ
  新ノード由来に差し替える。これで「ループ内で変換された値が親へ還流する」上り方向の
  フローが自然に出る。syn 2 では複合代入は
  `ExprBinary` + `*Assign` 系 `BinOp` (ExprAssignOp は無い)
- クロージャは `visit_expr_closure` を空実装にして再帰を止める (追わない宣言)

## impl メソッド対応の関数索引

- **ImplItemFn → ItemFn の正規化**: attrs / vis / sig / block は形が共通なので、
  メソッドを `ItemFn` に詰め替えれば後段 (ノード構築) を一本化できる
- **qualified 名 (`Foo::bar`) を一意キーの正**とし、素の名前はソース出現順の最初に
  解決するフォールバックにする (同名メソッドの impl 違いを区別する一意キー)。
  impl 文脈は self 型の最後のパスセグメント (`impl fmt::Display for Foo` → `Foo`)
- **「索引と本体は同じ走査範囲」が規約なら walker を1本にする** (1関心1visitor の
  意図的な例外として明記する)。list / parse / serve の3者が同じ walker を共有すれば
  「列挙された名前は必ず再発見できる」規約が一点で守れる
