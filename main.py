# Uygulamanın tamamını oluşturmak için gereken modülleri yeniden içe aktar
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import pyperclip

# Verilerin saklanacağı dizin ve dosya yolu
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "veriler.json")

# JSON verisi yoksa başlat
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

# JSON verisini yükle
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# JSON verisini kaydet
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Ana uygulama sınıfı
class KaynakUygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kaynak Yöneticisi")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")
        self.data = load_data()
        self.selected_group = None
        self.selected_subgroup = None

        self.setup_ui()

    def setup_ui(self):
        # Sol panel (gruplar)
        self.left_frame = tk.Frame(self, bg="#2e2e2e", width=200)
        self.left_frame.pack(side="left", fill="y")

        self.group_listbox = tk.Listbox(self.left_frame, bg="#2e2e2e", fg="white")
        self.group_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.group_listbox.bind("<<ListboxSelect>>", self.on_group_select)
        self.group_listbox.bind("<Button-3>", self.right_click_group)

        tk.Button(self.left_frame, text="+ Grup", command=self.add_group, bg="#3e3e3e", fg="white").pack(fill="x")

        # Sağ panel (alt gruplar ve içerik)
        self.right_frame = tk.Frame(self, bg="#2e2e2e")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.top_bar = tk.Frame(self.right_frame, bg="#2e2e2e")
        self.top_bar.pack(fill="x")

        self.search_entry = tk.Entry(self.top_bar)
        self.search_entry.pack(side="left", padx=5, pady=5)
        tk.Button(self.top_bar, text="Ara", command=self.search_content).pack(side="left", padx=5)

        self.add_subgroup_btn = tk.Button(self.top_bar, text="+ Alt Grup", command=self.add_subgroup)
        self.add_subgroup_btn.pack(side="left", padx=5)

        self.add_content_btn = tk.Button(self.top_bar, text="+ İçerik", command=self.add_content)
        self.add_content_btn.pack(side="left", padx=5)

        self.content_area = scrolledtext.ScrolledText(self.right_frame, bg="#1e1e1e", fg="white", wrap=tk.WORD)
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_groups()

    def refresh_groups(self):
        self.group_listbox.delete(0, tk.END)
        for group in self.data:
            self.group_listbox.insert(tk.END, group)

    def on_group_select(self, event):
        selection = self.group_listbox.curselection()
        if selection:
            group = self.group_listbox.get(selection[0])
            self.selected_group = group
            self.selected_subgroup = None
            self.show_contents()

    def show_contents(self):
        self.content_area.delete("1.0", tk.END)
        contents = []

        if self.selected_group:
            grup_data = self.data.get(self.selected_group, {})
            if isinstance(grup_data, dict):
                # Ana grup içeriği varsa göster
                ana_icerik = grup_data.get("_content", [])
                for item in ana_icerik:
                    contents.append(f"[{item['tip']}] {item['baslik']}\n{item['icerik']}\nAçıklama: {item['aciklama']}\n")

                # Alt grupları da göster
                for subgroup, subdata in grup_data.items():
                    if subgroup == "_content":
                        continue
                    for item in subdata:
                        contents.append(f"({subgroup}) [{item['tip']}] {item['baslik']}\n{item['icerik']}\nAçıklama: {item['aciklama']}\n")

        self.content_area.insert(tk.END, "\n\n".join(contents))

    def add_group(self):
        name = simpledialog.askstring("Grup Ekle", "Grup adı:")
        if name:
            self.data[name] = {}
            save_data(self.data)
            self.refresh_groups()

    def add_subgroup(self):
        if not self.selected_group:
            messagebox.showwarning("Uyarı", "Önce bir grup seçin.")
            return
        name = simpledialog.askstring("Alt Grup Ekle", "Alt grup adı:")
        if name:
            self.data[self.selected_group][name] = []
            save_data(self.data)
            self.show_contents()

    def add_content(self):
        if not self.selected_group:
            return

        icerik_pencere = tk.Toplevel(self)
        icerik_pencere.title("İçerik Ekle")
        icerik_pencere.configure(bg="#2e2e2e")
        icerik_pencere.geometry("400x400")

        tip = tk.StringVar(value="Kod")

        ttk.Radiobutton(icerik_pencere, text="Kod", variable=tip, value="Kod").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(icerik_pencere, text="Link", variable=tip, value="Link").pack(anchor="w", padx=10, pady=5)

        tk.Label(icerik_pencere, text="Başlık:", bg="#2e2e2e", fg="white").pack()
        baslik = tk.Entry(icerik_pencere)
        baslik.pack(fill="x", padx=10)

        tk.Label(icerik_pencere, text="İçerik:", bg="#2e2e2e", fg="white").pack()
        icerik_text = tk.Text(icerik_pencere, height=5)
        icerik_text.pack(fill="x", padx=10)

        tk.Label(icerik_pencere, text="Açıklama:", bg="#2e2e2e", fg="white").pack()
        aciklama = tk.Entry(icerik_pencere)
        aciklama.pack(fill="x", padx=10)

        def kaydet():
            yeni = {
                "tip": tip.get(),
                "baslik": baslik.get(),
                "icerik": icerik_text.get("1.0", tk.END).strip(),
                "aciklama": aciklama.get()
            }
            grup = self.data[self.selected_group]
            if self.selected_subgroup:
                grup[self.selected_subgroup].append(yeni)
            else:
                if "_content" not in grup:
                    grup["_content"] = []
                grup["_content"].append(yeni)
            save_data(self.data)
            self.show_contents()
            icerik_pencere.destroy()

        tk.Button(icerik_pencere, text="Kaydet", command=kaydet).pack(pady=10)

    def right_click_group(self, event):
        try:
            index = self.group_listbox.nearest(event.y)
            self.group_listbox.selection_clear(0, tk.END)
            self.group_listbox.selection_set(index)
            selected = self.group_listbox.get(index)

            menu = tk.Menu(self, tearoff=0, bg="#3e3e3e", fg="white")
            menu.add_command(label="Yeniden Adlandır", command=lambda: self.rename_group(selected))
            menu.add_command(label="Sil", command=lambda: self.delete_group(selected))
            menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def rename_group(self, group):
        new_name = simpledialog.askstring("Yeniden Adlandır", "Yeni isim:", initialvalue=group)
        if new_name:
            self.data[new_name] = self.data.pop(group)
            save_data(self.data)
            self.refresh_groups()

    def delete_group(self, group):
        if messagebox.askyesno("Sil", f"{group} grubunu silmek istiyor musunuz?"):
            del self.data[group]
            save_data(self.data)
            self.refresh_groups()

    def search_content(self):
        aranan = self.search_entry.get().lower()
        if not aranan:
            return
        results = []
        for grup, veriler in self.data.items():
            for alt, liste in veriler.items():
                if alt == "_content":
                    for item in liste:
                        if aranan in item["baslik"].lower() or aranan in item["aciklama"].lower():
                            results.append(f"[{grup}] {item['baslik']}")
                else:
                    for item in liste:
                        if aranan in item["baslik"].lower() or aranan in item["aciklama"].lower():
                            results.append(f"[{grup} > {alt}] {item['baslik']}")
        self.content_area.delete("1.0", tk.END)
        self.content_area.insert(tk.END, "\n".join(results))


# Uygulamayı başlat
app = KaynakUygulama()
app.mainloop()
