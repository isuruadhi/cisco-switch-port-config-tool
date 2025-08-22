import csv
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk, messagebox
from netmiko import ConnectHandler

def connect_device():
    return {
        'device_type': 'cisco_ios',
        'host': entry_ip.get(),
        'username': entry_user.get(),
        'password': entry_pass.get(),
    }

def show_port_config():
    iface_type = iface_var.get()
    port_num = entry_port.get()
    interface_id = f"{iface_type}{port_num}"

    try:
        with ConnectHandler(**connect_device()) as net_connect:
            command = f"show running-config interface {interface_id}"
            output = net_connect.send_command(command)
        messagebox.showinfo("Port Configuration", f"Current config for {interface_id}:\n\n{output}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def preview_config():
    iface_type = iface_var.get()
    port_num = entry_port.get()
    vlan_id = entry_vlan.get().strip()
    description = entry_desc.get()
    port_mode = mode_var.get()  # "Trunk" or "Access"
    additional_cmds_text = text_additional.get("1.0", tk.END).strip()
    interface_id = f"{iface_type}{port_num}"

    commands = [
        f"default interface {interface_id}",
        f"interface {interface_id}",
    ]

    if port_mode == "Trunk":
        commands += [
            "switchport mode trunk",
            f"switchport trunk native vlan {vlan_id}",
        ]
    else:  # Access
        commands += [
            "switchport mode access",
            f"switchport access vlan {vlan_id}",
        ]

    if vlan_id == "50":
        commands += [
            "switchport port-security maximum 2",
            "switchport port-security mac-address sticky"
        ]

    if vlan_id == "30":
        commands += [
            "switchport voice vlan 40"
        ]

    if description:
        commands.append(f"description {description}")

    if additional_cmds_text:
        additional_cmds = [line.strip() for line in additional_cmds_text.splitlines() if line.strip()]
        commands += additional_cmds

    commands += [
        "end",
        "write memory"
    ]

    preview_text = "\n".join(commands)
    if messagebox.askyesno("Preview Configuration", f"The following config will be applied:\n\n{preview_text}\n\nProceed?"):
        configure_switch(commands)

def configure_switch(commands):
    try:
        with ConnectHandler(**connect_device()) as net_connect:
            output = net_connect.send_config_set(commands)
        messagebox.showinfo("Success", f"Configuration applied successfully:\n{output}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Setup main window
root = tk.Tk()
root.title("Cisco Switch Port Config Tool")
root.geometry("500x520")
root.resizable(False, False)

# Use ttk styles for better look
style = ttk.Style(root)
style.theme_use('clam')

padding_options = {'padx': 10, 'pady': 5}

frame = ttk.Frame(root)
frame.pack(fill='both', expand=True, **padding_options)


# Username
ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", **padding_options)
entry_user = ttk.Entry(frame, width=30)
entry_user.grid(row=0, column=1, sticky="ew", **padding_options)

# Password
ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w", **padding_options)
entry_pass = ttk.Entry(frame, width=30, show="*")  # Hide typed chars
entry_pass.grid(row=1, column=1, sticky="ew", **padding_options)

# Switch IP
ttk.Label(frame, text="Switch IP:").grid(row=2, column=0, sticky="w", **padding_options)
entry_ip = ttk.Entry(frame, width=30)
entry_ip.grid(row=2, column=1, sticky="ew", **padding_options)

# Interface type
ttk.Label(frame, text="Interface Type:").grid(row=3, column=0, sticky="w", **padding_options)
iface_var = tk.StringVar(value="GigabitEthernet")
iface_menu = ttk.OptionMenu(frame, iface_var, "GigabitEthernet", "FastEthernet", "GigabitEthernet")
iface_menu.grid(row=3, column=1, sticky="ew", **padding_options)

# Port number
ttk.Label(frame, text="Port Number:").grid(row=4, column=0, sticky="w", **padding_options)
entry_port = ttk.Entry(frame, width=30)
entry_port.grid(row=4, column=1, sticky="ew", **padding_options)

# Port mode
ttk.Label(frame, text="Port Mode:").grid(row=5, column=0, sticky="w", **padding_options)
mode_var = tk.StringVar(value="Trunk")
mode_menu = ttk.OptionMenu(frame, mode_var, "Trunk", "Trunk", "Access")
mode_menu.grid(row=5, column=1, sticky="ew", **padding_options)

# VLAN ID
ttk.Label(frame, text="VLAN ID:").grid(row=6, column=0, sticky="w", **padding_options)
entry_vlan = ttk.Entry(frame, width=30)
entry_vlan.grid(row=6, column=1, sticky="ew", **padding_options)

# Description
ttk.Label(frame, text="Description:").grid(row=7, column=0, sticky="w", **padding_options)
entry_desc = ttk.Entry(frame, width=30)
entry_desc.grid(row=7, column=1, sticky="ew", **padding_options)

# Additional commands label and text box with scrollbar
ttk.Label(frame, text="Additional Commands (one per line):").grid(row=8, column=0, sticky="nw", **padding_options)
text_additional = tk.Text(frame, width=35, height=7, wrap='word', relief='sunken', borderwidth=1)
text_additional.grid(row=8, column=1, sticky="ew", **padding_options)

scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text_additional.yview)
scrollbar.grid(row=9, column=2, sticky='ns', pady=5)
text_additional['yscrollcommand'] = scrollbar.set

# Buttons frame
btn_frame = ttk.Frame(frame)
btn_frame.grid(row=10, column=0, columnspan=3, pady=20)

btn_view = ttk.Button(btn_frame, text="View Current Config", command=show_port_config)
btn_view.pack(side='left', padx=10)

btn_apply = ttk.Button(btn_frame, text="Preview & Apply Config", command=preview_config)
btn_apply.pack(side='left', padx=10)

# Configure grid weights for resizing behavior
frame.columnconfigure(1, weight=1)

def bulk_upload():
    filename = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not filename:
        return

    configs_list = []  # Store tuples (switch_ip, interface_id, commands)

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            interface_id = f"{row['iface_type']}{row['port_num']}"
            commands = [
                f"default interface {interface_id}",
                f"interface {interface_id}",
            ]

            port_mode = row['port_mode'].strip()
            vlan_id = row['vlan_id'].strip()
            description = row.get('description', '').strip()
            additional_cmds_text = row.get('additional_cmds', '').strip()

            if port_mode.lower() == "trunk":
                commands += [
                    "switchport mode trunk",
                    f"switchport trunk native vlan {vlan_id}",
                ]
            else:
                commands += [
                    "switchport mode access",
                    f"switchport access vlan {vlan_id}",
                ]

            if vlan_id == "50":
                commands += [
                    "switchport port-security maximum 2",
                    "switchport port-security mac-address sticky"
                ]

            if description:
                commands.append(f"description {description}")

            if additional_cmds_text:
                additional_cmds = [cmd.strip() for cmd in additional_cmds_text.split(';') if cmd.strip()]
                commands += additional_cmds

            commands += [
                "end",
                "write memory"
            ]

            configs_list.append((row['switch_ip'], interface_id, commands))

    # Create Preview Window
    preview_window = tk.Toplevel(root)
    preview_window.title("Bulk Upload Preview")
    preview_window.geometry("650x450")

    # Text box with scrollbar
    text_frame = ttk.Frame(preview_window)
    text_frame.pack(fill='both', expand=True, padx=10, pady=10)

    text_preview = tk.Text(text_frame, wrap='word')
    text_preview.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_preview.yview)
    scrollbar.pack(side='right', fill='y')
    text_preview.configure(yscrollcommand=scrollbar.set)

    # Populate preview
    for switch_ip, interface_id, commands in configs_list:
        text_preview.insert(tk.END, f"Switch: {switch_ip}\n")
        text_preview.insert(tk.END, "\n".join(commands) + "\n")
        text_preview.insert(tk.END, "-"*50 + "\n")

    # Buttons frame inside preview window
    btn_frame_preview = ttk.Frame(preview_window)
    btn_frame_preview.pack(pady=10)

    def apply_all():
        success_count = 0
        failure_count = 0
        errors = []

        for switch_ip, interface_id, commands in configs_list:
            try:
                device = {
                    'device_type': 'cisco_ios',
                    'host': switch_ip,
                    'username': entry_user.get(),
                    'password': entry_pass.get(),
                }
                with ConnectHandler(**device) as net_connect:
                    net_connect.send_config_set(commands)
                success_count += 1
            except Exception as e:
                failure_count += 1
                errors.append(f"{switch_ip} {interface_id}: {e}")

        summary = f"Bulk Upload Complete:\nSuccessful: {success_count}\nFailed: {failure_count}"
        if errors:
            summary += "\n\nErrors:\n" + "\n".join(errors)

        messagebox.showinfo("Bulk Upload Result", summary)
        preview_window.destroy()

    ttk.Button(btn_frame_preview, text="Apply to All", command=apply_all).pack(side='left', padx=10)
    ttk.Button(btn_frame_preview, text="Cancel", command=preview_window.destroy).pack(side='left', padx=10)

btn_bulk = ttk.Button(btn_frame, text="Bulk Upload CSV", command=bulk_upload)
btn_bulk.pack(side='left', padx=10)

root.mainloop()
