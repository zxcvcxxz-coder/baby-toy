import time
from app import BabyToyApp

def show_welcome_message():
    """起動時のコンソール案内を表示"""
    print("========================================")
    print(" 【GUIアプリ版 テスト】")
    print(" 5秒後にキーフックが有効になります。")
    print(" ・画面が出たらキーをバシバシ押してみてください")
    print(" ・終了するには 'q' 'u' 'i' 't' を順番に")
    print("========================================")

    for i in range(5, 0, -1):
        print(f"開始まで... {i}秒")
        time.sleep(1)

    print("\n【キーフック開始】システムキーを含めブロック中...")


def main():
    show_welcome_message()
    app = BabyToyApp()
    app.run()


if __name__ == "__main__":
    main()