"""Convert graph SVGs and LaTeX-generated SVGs to PNG."""

import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cairosvg

MODE_GRAPH = "グラフSVG → PNG"
MODE_LATEX_SVG = "LaTeX SVG → PNG"


class SvgToPngApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SVG → PNG 変換")
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value=MODE_GRAPH)
        self.svg_path = tk.StringVar()
        self.png_path = tk.StringVar()
        self.dpi = tk.StringVar(value="300")
        self.output_width = tk.StringVar()

        frame = ttk.Frame(root, padding=16)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="変換モード").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        mode_menu = ttk.Combobox(
            frame,
            textvariable=self.mode,
            values=(MODE_GRAPH, MODE_LATEX_SVG),
            state="readonly",
            width=28,
        )
        mode_menu.grid(row=0, column=1, sticky="w", pady=5)
        mode_menu.bind("<<ComboboxSelected>>", self.update_mode)

        self.svg_label = ttk.Label(frame, text="グラフSVG")
        self.svg_label.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Entry(frame, textvariable=self.svg_path, width=48).grid(
            row=1, column=1, sticky="ew", pady=5
        )
        ttk.Button(frame, text="参照…", command=self.choose_svg).grid(
            row=1, column=2, padx=(8, 0), pady=5
        )

        ttk.Label(frame, text="保存先 PNG").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Entry(frame, textvariable=self.png_path, width=48).grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="参照…", command=self.choose_png).grid(
            row=2, column=2, padx=(8, 0), pady=5
        )

        ttk.Label(frame, text="解像度 (DPI)").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Spinbox(frame, from_=1, to=2400, textvariable=self.dpi, width=10).grid(
            row=3, column=1, sticky="w", pady=5
        )
        ttk.Label(frame, text="標準: 300 DPI").grid(row=3, column=1, sticky="w", padx=(100, 0), pady=5)

        ttk.Label(frame, text="出力幅 (px)").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=5)
        ttk.Entry(frame, textvariable=self.output_width, width=12).grid(
            row=4, column=1, sticky="w", pady=5
        )
        ttk.Label(frame, text="空欄ならDPIから計算").grid(
            row=4, column=1, sticky="w", padx=(100, 0), pady=5
        )

        ttk.Button(frame, text="PNGに変換", command=self.convert).grid(
            row=5, column=0, columnspan=3, sticky="ew", pady=(14, 0)
        )
        self.update_mode()

    def update_mode(self, _event=None) -> None:
        if self.mode.get() == MODE_GRAPH:
            self.svg_label.configure(text="グラフSVG")
        else:
            self.svg_label.configure(text="LaTeXで作成したSVG")

    def choose_svg(self) -> None:
        if self.mode.get() == MODE_GRAPH:
            title = "グラフSVGを選択"
        else:
            title = "LaTeXで作成したSVGを選択"
        path = filedialog.askopenfilename(
            title=title,
            filetypes=[("SVGファイル", "*.svg"), ("すべてのファイル", "*.*")],
        )
        if path:
            self.svg_path.set(path)
            if not self.png_path.get():
                self.png_path.set(str(Path(path).with_suffix(".png")))

    def choose_png(self) -> None:
        initial = Path(self.png_path.get()).name if self.png_path.get() else "output.png"
        path = filedialog.asksaveasfilename(
            title="PNGの保存先を選択",
            initialfile=initial,
            defaultextension=".png",
            filetypes=[("PNG画像", "*.png")],
        )
        if path:
            self.png_path.set(path)

    def convert(self) -> None:
        source = Path(self.svg_path.get()).expanduser()
        destination = Path(self.png_path.get()).expanduser()

        if not source.is_file() or source.suffix.lower() != ".svg":
            messagebox.showerror("入力エラー", "変換するSVGファイルを選択してください。", parent=self.root)
            return
        if not destination.name:
            messagebox.showerror("入力エラー", "PNGの保存先を指定してください。", parent=self.root)
            return
        try:
            dpi = int(self.dpi.get())
            if not 1 <= dpi <= 2400:
                raise ValueError
        except ValueError:
            messagebox.showerror("入力エラー", "DPIは1〜2400の整数で指定してください。", parent=self.root)
            return

        output_width = None
        if self.output_width.get().strip():
            try:
                output_width = int(self.output_width.get())
                if not 1 <= output_width <= 30000:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "入力エラー", "出力幅は1〜30000の整数で指定してください。", parent=self.root
                )
                return

        if destination.suffix.lower() != ".png":
            destination = destination.with_suffix(".png")
            self.png_path.set(str(destination))

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if self.mode.get() == MODE_GRAPH:
                self.convert_graph_svg(source, destination, dpi, output_width)
            else:
                self.convert_latex_svg(source, destination, dpi, output_width)
        except Exception as error:
            messagebox.showerror("変換エラー", f"PNGへの変換に失敗しました。\n{error}", parent=self.root)
            return

        messagebox.showinfo("変換完了", f"PNGを保存しました。\n{destination}", parent=self.root)

    @staticmethod
    def convert_graph_svg(
        source: Path, destination: Path, dpi: int, output_width: int | None
    ) -> None:
        if b"<foreignObject" in source.read_bytes():
            raise ValueError(
                "このSVGはHTMLを埋め込むforeignObject形式です。\n"
                "変換モードを「LaTeX SVG → PNG」に切り替えてください。"
            )
        if output_width is None:
            cairosvg.svg2png(
                url=str(source), write_to=str(destination), scale=dpi / 96.0
            )
        else:
            cairosvg.svg2png(
                url=str(source), write_to=str(destination), output_width=output_width
            )

    @staticmethod
    def convert_latex_svg(
        source: Path, destination: Path, dpi: int, output_width: int | None
    ) -> None:
        """Rasterize the original SVG in Chromium, preserving its fonts and HTML."""
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise RuntimeError(
                "Playwrightがインストールされていません。requirements.txtを再インストールしてください。"
            ) from error

        device_scale = dpi / 96.0

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(
                    viewport={"width": 1280, "height": 720},
                    device_scale_factor=device_scale,
                )
                page.goto(source.resolve().as_uri(), wait_until="load")
                page.evaluate("() => document.fonts && document.fonts.ready")
                svg = page.locator("svg").first
                dimensions = svg.evaluate(
                    "node => { const r = node.getBoundingClientRect(); "
                    "return {width: r.width, height: r.height}; }"
                )
                natural_width = dimensions["width"]
                natural_height = dimensions["height"]
                if not natural_width or not natural_height:
                    raise ValueError("SVGの幅と高さを読み取れませんでした。")

                css_width = (
                    output_width / device_scale if output_width is not None else natural_width
                )
                css_height = css_width * natural_height / natural_width
                page.set_viewport_size(
                    {
                        "width": max(1, math.ceil(css_width)),
                        "height": max(1, math.ceil(css_height)),
                    }
                )
                svg.evaluate(
                    "(node, width) => { node.style.width = `${width}px`; "
                    "node.style.height = 'auto'; }",
                    css_width,
                )
                page.evaluate("() => document.fonts && document.fonts.ready")
                svg.screenshot(
                    path=str(destination), scale="device", omit_background=True
                )
                browser.close()
        except PlaywrightError as error:
            raise RuntimeError(
                "Chromiumが使えません。初回セットアップで次を実行してください:\n"
                "python3 -m playwright install chromium\n\n"
                f"詳細: {error}"
            ) from error

def main() -> None:
    root = tk.Tk()
    SvgToPngApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
