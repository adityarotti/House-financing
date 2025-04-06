import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os

class HouseCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("House Cost Calculator")
        self.root.geometry("1700x1200")

        # Storage for saved scenarios
        self.saved_scenarios = {}
        self.current_scenario_name = tk.StringVar(value="Default")
        self.current_scenario_data = {}

        # Variables for sliders/inputs
        self.raw_house_cost = tk.DoubleVar(value=350000)
        self.mortgage_rate = tk.DoubleVar(value=3.8)
        self.yearly_repayment = tk.DoubleVar(value=5)
        self.nebenkosten = tk.DoubleVar(value=400)
        self.inflation = tk.DoubleVar(value=2.7)
        self.house_inflation = tk.DoubleVar(value=2.7)
        self.loan_period = tk.IntVar(value=30)
        self.down_payment = tk.DoubleVar(value=35000)
        self.broker_commission = tk.DoubleVar(value=3.57)
        self.notary = tk.DoubleVar(value=1.5)
        self.land_registry = tk.DoubleVar(value=0.5)
        self.land_transfer_tax = tk.DoubleVar(value=5.0)
        self.monthly_rent = tk.DoubleVar(value=1300)

        # Display variables
        self.raw_house_cost_display = tk.StringVar(value=f"{self.raw_house_cost.get():.1f}")
        self.mortgage_rate_display = tk.StringVar(value=f"{self.mortgage_rate.get():.1f}")
        self.monthly_rent_display = tk.StringVar(value=f"{self.monthly_rent.get():.1f}")
        self.yearly_repayment_display = tk.StringVar(value=f"{self.yearly_repayment.get():.1f}")
        self.nebenkosten_display = tk.StringVar(value=f"{self.nebenkosten.get():.1f}")
        self.inflation_display = tk.StringVar(value=f"{self.inflation.get():.1f}")
        self.house_inflation_display = tk.StringVar(value=f"{self.house_inflation.get():.1f}")
        self.loan_period_display = tk.StringVar(value=f"{self.loan_period.get():.1f}")
        self.down_payment_display = tk.StringVar(value=f"{self.down_payment.get():.1f}")
        self.broker_commission_display = tk.StringVar(value=f"{self.broker_commission.get():.1f}")
        self.notary_display = tk.StringVar(value=f"{self.notary.get():.1f}")
        self.land_registry_display = tk.StringVar(value=f"{self.land_registry.get():.1f}")
        self.land_transfer_tax_display = tk.StringVar(value=f"{self.land_transfer_tax.get():.1f}")

        # Result display variables
        self.monthly_repayment_display = tk.StringVar(value="Monthly Repayment: $0.0")
        self.upfront_costs_display = tk.StringVar(value="Upfront Costs: $0.0")
        self.extra_costs_display = tk.StringVar(value="Total Extra Costs: $0.0")
        self.eff_house_cost_display = tk.StringVar(value="Effective house costs: $0.0")
        self.loan_amount_display = tk.StringVar(value="Loan amount: $0.0")
        self.buying_cost_display = tk.StringVar(value="Buying cost: $0.0")
        self.show_down_payment = tk.StringVar(value="Down payment: $0.0")
        self.show_yearly_payment = tk.StringVar(value="Yearly payment: $0.0")

        # Input mode selection
        self.input_mode = tk.StringVar(value="entries")

        # Create main frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create input controls frame
        self.create_input_controls()

        # Create single figure with two subplots
        self.figure = plt.figure(figsize=(12, 8))
        self.ax1 = self.figure.add_subplot(2, 1, 1)  # Top subplot
        self.ax2 = self.figure.add_subplot(2, 1, 2)  # Bottom subplot
        self.ax1.sharex(self.ax2)  # Share x-axis

        # Create canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.main_frame)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.main_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create scenario management controls
        self.create_scenario_controls()

        # Create info box
        self.create_info_box()

        # Load any saved scenarios
        self.load_scenarios()

        # Initial plot
        self.update_plots()

    def create_scenario_controls(self):
        """Create controls for managing scenarios"""
        scenario_frame = ttk.LabelFrame(self.input_frame, text="Scenario Management", padding=10)
        scenario_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Scenario name entry
        ttk.Label(scenario_frame, text="Scenario Name:").grid(row=0, column=0, sticky=tk.W)
        self.scenario_name_entry = ttk.Entry(scenario_frame, textvariable=self.current_scenario_name)
        self.scenario_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        # Buttons frame
        btn_frame = ttk.Frame(scenario_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)

        # Save button
        ttk.Button(btn_frame, text="Save", command=self.save_scenario).pack(side=tk.LEFT, padx=5)

        # Load button
        ttk.Button(btn_frame, text="Load", command=self.load_scenario_dialog).pack(side=tk.LEFT, padx=5)

        # Compare button
        ttk.Button(btn_frame, text="Compare", command=self.compare_scenarios).pack(side=tk.LEFT, padx=5)

        # Delete button
        ttk.Button(btn_frame, text="Delete", command=self.delete_scenario).pack(side=tk.LEFT, padx=5)

    def create_info_box(self):
        """Create a decorated box with vertically ordered labels"""
        self.info_box = ttk.LabelFrame(self.input_frame, text="Cost Summary", padding=(10, 5), relief=tk.RIDGE)
        self.info_box.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10, ipady=5)

        # Configure style
        style = ttk.Style()
        style.configure('Info.TLabelframe', background='#f0f0f0')
        style.configure('Info.TLabelframe.Label', font=('Helvetica', 15, 'bold'))

        # Vertical layout of labels
        fontsize=15
        ttk.Label(self.info_box, textvariable=self.loan_amount_display, font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
        ttk.Label(self.info_box, textvariable=self.buying_cost_display, font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
        ttk.Label(self.info_box, textvariable=self.show_down_payment, font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
        ttk.Label(self.info_box, textvariable=self.upfront_costs_display, font=('Helvetica', fontsize)).pack(anchor=tk.W,
                                                                                                      pady=2)
        ttk.Label(self.info_box, textvariable=self.monthly_repayment_display, font=('Helvetica', fontsize)).pack(anchor=tk.W,
                                                                                                          pady=2)
        ttk.Label(self.info_box, textvariable=self.show_yearly_payment, font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
        ttk.Label(self.info_box, textvariable=self.extra_costs_display, font=('Helvetica', fontsize, 'bold')).pack(anchor=tk.W,
                                                                                                            pady=2)
        ttk.Label(self.info_box, textvariable=self.eff_house_cost_display, font=('Helvetica', fontsize, 'bold')).pack(
            anchor=tk.W,
            pady=2)

        # Separator
        ttk.Separator(self.info_box, orient='horizontal').pack(fill=tk.X, pady=5)

    def create_input_controls(self):
        # Main frame for input controls
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Input mode selection
        mode_frame = ttk.Frame(self.input_frame)
        mode_frame.pack(pady=10)
        ttk.Label(mode_frame, text="Input Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Text Entries", variable=self.input_mode, value="entries",
                        command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Sliders", variable=self.input_mode, value="sliders",
                        command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)


        # Frame for sliders
        self.entries_frame = ttk.Frame(self.input_frame)
        self.entries_frame.pack(fill=tk.Y)

        # Frame for entry fields (initially hidden)
        self.sliders_frame = ttk.Frame(self.input_frame)

        # Create both sliders and entries
        self.create_entries()
        self.create_sliders()

    def create_sliders(self):
        sliders = [
            ("House Cost ($)", self.raw_house_cost, 100000, 1000000, self.raw_house_cost_display),
            ("Mortgage Rate (%)", self.mortgage_rate, 1, 10, self.mortgage_rate_display),
            ("Down payment ($)", self.down_payment, 0, 100000, self.down_payment_display),
            ("Broker commission (%)", self.broker_commission, 0, 10, self.broker_commission_display),
            ("Notary (%)", self.notary, 0, 5, self.notary_display),
            ("Land registry (%)", self.land_registry, 0, 5, self.land_registry_display),
            ("Land transfer tax (%)", self.land_transfer_tax, 0, 10, self.land_transfer_tax_display),
            ("Yearly Repayment (%)", self.yearly_repayment, 0, 10, self.yearly_repayment_display),
            ("Loan Period (Years)", self.loan_period, 10, 50, self.loan_period_display),
            ("Other Costs ($)", self.nebenkosten, 0, 2000, self.nebenkosten_display),
            ("Monthly Rent ($)", self.monthly_rent, 500, 3000, self.monthly_rent_display),
            ("Inflation (%)", self.inflation, 0, 10, self.inflation_display),
            ("House Inflation (%)", self.house_inflation, 0, 10, self.house_inflation_display),
        ]

        for label, var, min_val, max_val, display_var in sliders:
            slider_frame = ttk.Frame(self.sliders_frame)
            slider_frame.pack(pady=5)

            ttk.Label(slider_frame, text=label).pack(side=tk.LEFT, padx=5)

            slider = ttk.Scale(
                slider_frame,
                from_=min_val,
                to=max_val,
                orient=tk.HORIZONTAL,
                variable=var,
                length=200,
                command=lambda value, v=var, dv=display_var: self.update_slider_display(v, dv),
            )
            slider.pack(side=tk.LEFT)

            ttk.Label(slider_frame, textvariable=display_var).pack(side=tk.LEFT, padx=5)

    def create_entries(self):
        entries = [
            ("House Cost ($)", self.raw_house_cost, self.raw_house_cost_display),
            ("Mortgage Rate (%)", self.mortgage_rate, self.mortgage_rate_display),
            ("Down payment ($)", self.down_payment, self.down_payment_display),
            ("Broker commission (%)", self.broker_commission, self.broker_commission_display),
            ("Notary (%)", self.notary, self.notary_display),
            ("Land registry (%)", self.land_registry, self.land_registry_display),
            ("Land transfer tax (%)", self.land_transfer_tax, self.land_transfer_tax_display),
            ("Yearly Repayment (%)", self.yearly_repayment, self.yearly_repayment_display),
            ("Loan Period (Years)", self.loan_period, self.loan_period_display),
            ("Other Costs ($)", self.nebenkosten, self.nebenkosten_display),
            ("Monthly Rent ($)", self.monthly_rent, self.monthly_rent_display),
            ("Inflation (%)", self.inflation, self.inflation_display),
            ("House Inflation (%)", self.house_inflation, self.house_inflation_display),
        ]

        for label, var, display_var in entries:
            entry_frame = ttk.Frame(self.entries_frame)
            entry_frame.pack(pady=5)

            ttk.Label(entry_frame, text=label).pack(side=tk.LEFT, padx=5)

            entry = ttk.Entry(
                entry_frame,
                textvariable=display_var,
                width=10
            )
            entry.pack(side=tk.LEFT)
            # entry.bind("<Return>", lambda e, v=var, dv=display_var: self.update_from_entry(v, dv))
            entry.bind("<FocusOut>", lambda e, v=var, dv=display_var: self.update_from_entry(v, dv))

    def toggle_input_mode(self):
        if self.input_mode.get() == "entries":
            self.sliders_frame.pack_forget()
            self.entries_frame.pack(fill=tk.Y)
        else:
            self.entries_frame.pack_forget()
            self.sliders_frame.pack(fill=tk.Y)
        self.update_plots()

    def update_slider_display(self, var, display_var):
        display_var.set(f"{var.get():.1f}")
        self.update_plots()

    def update_from_entry(self, var, display_var):
        try:
            value = float(display_var.get())
            var.set(value)
            self.update_plots()
        except ValueError:
            display_var.set(f"{var.get():.1f}")

    def get_current_scenario_data(self):
        """Get all current input values as a dictionary"""
        return {
            'raw_house_cost': self.raw_house_cost.get(),
            'mortgage_rate': self.mortgage_rate.get(),
            'yearly_repayment': self.yearly_repayment.get(),
            'nebenkosten': self.nebenkosten.get(),
            'inflation': self.inflation.get(),
            'house_inflation': self.house_inflation.get(),
            'loan_period': self.loan_period.get(),
            'down_payment': self.down_payment.get(),
            'broker_commission': self.broker_commission.get(),
            'notary': self.notary.get(),
            'land_registry': self.land_registry.get(),
            'land_transfer_tax': self.land_transfer_tax.get(),
            'monthly_rent': self.monthly_rent.get(),
            'timestamp': str(np.datetime64('now'))
        }

    def save_scenario(self):
        """Save current inputs as a named scenario"""
        scenario_name = self.current_scenario_name.get().strip()
        if not scenario_name:
            messagebox.showerror("Error", "Please enter a scenario name")
            return

        self.saved_scenarios[scenario_name] = self.get_current_scenario_data()
        self.save_scenarios_to_file()
        messagebox.showinfo("Saved", f"Scenario '{scenario_name}' saved successfully")

    def load_scenario_dialog(self):
        """Show dialog to select and load a scenario"""
        if not self.saved_scenarios:
            messagebox.showinfo("Info", "No saved scenarios found")
            return

        load_window = tk.Toplevel(self.root)
        load_window.title("Load Scenario")

        ttk.Label(load_window, text="Select Scenario:").pack(pady=5)

        scenario_listbox = tk.Listbox(load_window, height=10, width=30)
        scenario_listbox.pack(pady=5)

        for name in sorted(self.saved_scenarios.keys()):
            scenario_listbox.insert(tk.END, name)

        def load_selected():
            selection = scenario_listbox.curselection()
            if selection:
                scenario_name = scenario_listbox.get(selection[0])
                self.load_scenario(scenario_name)
                load_window.destroy()

        ttk.Button(load_window, text="Load", command=load_selected).pack(pady=5)

    def load_scenario(self, scenario_name):
        """Load a saved scenario"""
        if scenario_name not in self.saved_scenarios:
            messagebox.showerror("Error", f"Scenario '{scenario_name}' not found")
            return

        scenario_data = self.saved_scenarios[scenario_name]

        # Update all variables
        self.raw_house_cost.set(scenario_data['raw_house_cost'])
        self.mortgage_rate.set(scenario_data['mortgage_rate'])
        self.yearly_repayment.set(scenario_data['yearly_repayment'])
        self.nebenkosten.set(scenario_data['nebenkosten'])
        self.inflation.set(scenario_data['inflation'])
        self.house_inflation.set(scenario_data['house_inflation'])
        self.loan_period.set(scenario_data['loan_period'])
        self.down_payment.set(scenario_data['down_payment'])
        self.broker_commission.set(scenario_data['broker_commission'])
        self.notary.set(scenario_data['notary'])
        self.land_registry.set(scenario_data['land_registry'])
        self.land_transfer_tax.set(scenario_data['land_transfer_tax'])
        self.monthly_rent.set(scenario_data['monthly_rent'])

        # Update display variables
        self.raw_house_cost_display.set(f"{scenario_data['raw_house_cost']:.1f}")
        self.mortgage_rate_display.set(f"{scenario_data['mortgage_rate']:.1f}")
        self.yearly_repayment_display.set(f"{scenario_data['yearly_repayment']:.1f}")
        self.nebenkosten_display.set(f"{scenario_data['nebenkosten']:.1f}")
        self.inflation_display.set(f"{scenario_data['inflation']:.1f}")
        self.house_inflation_display.set(f"{scenario_data['house_inflation']:.1f}")
        self.loan_period_display.set(f"{scenario_data['loan_period']:.1f}")
        self.down_payment_display.set(f"{scenario_data['down_payment']:.1f}")
        self.broker_commission_display.set(f"{scenario_data['broker_commission']:.1f}")
        self.notary_display.set(f"{scenario_data['notary']:.1f}")
        self.land_registry_display.set(f"{scenario_data['land_registry']:.1f}")
        self.land_transfer_tax_display.set(f"{scenario_data['land_transfer_tax']:.1f}")
        self.monthly_rent_display.set(f"{scenario_data['monthly_rent']:.1f}")

        self.current_scenario_name.set(scenario_name)
        self.update_plots()

    def delete_scenario(self):
        """Delete the currently loaded scenario"""
        scenario_name = self.current_scenario_name.get()
        if scenario_name not in self.saved_scenarios:
            messagebox.showerror("Error", f"Scenario '{scenario_name}' not found")
            return

        if messagebox.askyesno("Confirm", f"Delete scenario '{scenario_name}'?"):
            del self.saved_scenarios[scenario_name]
            self.save_scenarios_to_file()
            messagebox.showinfo("Deleted", f"Scenario '{scenario_name}' deleted")
            self.current_scenario_name.set("Default")

    def compare_scenarios(self):
        """Compare multiple saved scenarios by showing their cost summaries side by side"""
        if len(self.saved_scenarios) < 2:
            messagebox.showinfo("Info", "Need at least 2 scenarios to compare")
            return

        compare_window = tk.Toplevel(self.root)
        compare_window.title("Compare Scenarios")
        compare_window.geometry("1000x600")

        # Main frame for comparison
        main_frame = ttk.Frame(compare_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scenario selection frame
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=5)

        ttk.Label(selection_frame, text="Select Scenarios:").pack(side=tk.LEFT)

        scenario_vars = []
        for name in sorted(self.saved_scenarios.keys()):
            var = tk.BooleanVar(value=True)
            scenario_vars.append((name, var))
            ttk.Checkbutton(selection_frame, text=name, variable=var).pack(side=tk.LEFT, padx=5)

        # Frame for cost summaries
        summaries_frame = ttk.Frame(main_frame)
        summaries_frame.pack(fill=tk.BOTH, expand=True)

        def update_comparison():
            # Clear previous summaries
            for widget in summaries_frame.winfo_children():
                widget.destroy()

            selected_scenarios = [name for name, var in scenario_vars if var.get()]
            if len(selected_scenarios) < 2:
                messagebox.showerror("Error", "Select at least 2 scenarios to compare")
                return

            # Create a frame for each scenario's summary
            for i, scenario_name in enumerate(selected_scenarios):
                scenario_data = self.saved_scenarios[scenario_name]

                # Run calculations for this scenario
                raw_house_cost = scenario_data['raw_house_cost']
                mortgage_rate = scenario_data['mortgage_rate']
                yearly_repayment_perc = scenario_data['yearly_repayment']
                yearly_repayment = raw_house_cost * yearly_repayment_perc / 100.
                loan_period = scenario_data['loan_period']
                down_payment = scenario_data['down_payment']
                broker_commission = scenario_data['broker_commission']
                notary = scenario_data['notary']
                land_registry = scenario_data['land_registry']
                land_transfer_tax = scenario_data['land_transfer_tax']
                nebenkosten = scenario_data["nebenkosten"]

                # Calculate costs
                buy_cost_perc = (broker_commission + notary + land_registry + land_transfer_tax) / 100.
                misc_costs = raw_house_cost * buy_cost_perc
                upfront_costs = misc_costs + down_payment
                loan_amount = raw_house_cost - down_payment

                monthly_repayment = loan_amount * (mortgage_rate / 100. / 12.) / (
                        1 - (1 + mortgage_rate / 100. / 12) ** (-12 * loan_period))

                # Calculate total interest
                months = np.linspace(1, loan_period * 12, loan_period * 12)
                repayments = [monthly_repayment] * len(months)
                for j, m in enumerate(months):
                    if m % 12 == 0:
                        repayments[j] += yearly_repayment

                interest_repayment = (loan_amount - np.cumsum(repayments)) * mortgage_rate / 12 / 100
                interest_repayment[interest_repayment < 0] = 0
                principle_repayment = np.array(repayments) - interest_repayment
                principle_repayment[np.cumsum(principle_repayment) > loan_amount] = 0
                total_repayment = interest_repayment + principle_repayment
                extra_cost = misc_costs + max(np.cumsum(interest_repayment))

                # Create summary frame for this scenario
                scenario_frame = ttk.LabelFrame(summaries_frame, text=scenario_name, padding=10)
                scenario_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Add summary labels
                fontsize=15
                ttk.Label(scenario_frame, text=f"House Cost: ${raw_house_cost:,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Down Payment: ${down_payment:,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Loan Amount: ${loan_amount:,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Mortgage Rate: {mortgage_rate:.2f}%", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Loan Period: {loan_period} years", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Monthly Repayment: ${monthly_repayment:,.2f} [{monthly_repayment + nebenkosten:,.2f}]", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Yearly Repayment: ${yearly_repayment:,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Upfront Costs: ${upfront_costs:,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Total Interest: ${max(np.cumsum(interest_repayment)):,.2f}", font=('Helvetica', fontsize)).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Effective house Cost: ${extra_cost + raw_house_cost:,.2f}", font=('Helvetica', fontsize, 'bold')).pack(anchor=tk.W, pady=2)
                ttk.Label(scenario_frame, text=f"Extra Cost %: ${extra_cost:,.2f} [{extra_cost * 100 / raw_house_cost:.1f}%]", font=('Helvetica', fontsize, 'bold')).pack(anchor=tk.W, pady=2)

        # Update button
        update_button = ttk.Button(main_frame, text="Update Comparison", command=update_comparison)
        update_button.pack(pady=5)

        # Initial comparison
        update_comparison()

    def save_scenarios_to_file(self):
        """Save scenarios to a JSON file"""
        with open('house_calc_scenarios.json', 'w') as f:
            json.dump(self.saved_scenarios, f, indent=2)

    def load_scenarios(self):
        """Load scenarios from a JSON file"""
        if os.path.exists('house_calc_scenarios.json'):
            try:
                with open('house_calc_scenarios.json', 'r') as f:
                    self.saved_scenarios = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load scenarios: {str(e)}")

    def update_plots(self):
        # Get values from variables
        raw_house_cost = self.raw_house_cost.get()
        mortgage_rate = self.mortgage_rate.get()
        monthly_rent = self.monthly_rent.get()
        yearly_repayment_perc = self.yearly_repayment.get()
        yearly_repayment = raw_house_cost * yearly_repayment_perc / 100.
        nebenkosten = self.nebenkosten.get()
        inflation = self.inflation.get()
        house_inflation = self.house_inflation.get()
        loan_period = self.loan_period.get()
        down_payment = self.down_payment.get()
        broker_commission = self.broker_commission.get()
        notary = self.notary.get()
        land_registry = self.land_registry.get()
        land_transfer_tax = self.land_transfer_tax.get()

        # Calculations
        buy_cost_perc = (broker_commission + notary + land_registry + land_transfer_tax) / 100.
        misc_costs = raw_house_cost * buy_cost_perc
        upfront_costs = misc_costs + down_payment
        loan_amount = raw_house_cost - down_payment

        monthly_repayment = loan_amount * (mortgage_rate / 100. / 12.) / (
                1 - (1 + mortgage_rate / 100. / 12) ** (-12 * loan_period))

        # Update labels with better formatting
        self.buying_cost_display.set(f"Buying Cost: ${misc_costs:,.2f}")
        self.show_down_payment.set(f"Down Payment: ${down_payment:,.2f}")
        self.show_yearly_payment.set(f"Yearly Payment: ${yearly_repayment:,.2f}")
        self.loan_amount_display.set(f"Loan Amount: ${loan_amount:,.2f}")
        self.monthly_repayment_display.set(f"Monthly Repayment: ${monthly_repayment:,.2f}")
        self.upfront_costs_display.set(f"Upfront Costs: ${upfront_costs:,.2f}")

        months = np.linspace(1, loan_period * 12, loan_period * 12)
        repayments = [monthly_repayment] * len(months)
        for i, m in enumerate(months):
            if m % 12 == 0:
                repayments[i] += yearly_repayment

        interest_repayment = (loan_amount - np.cumsum(repayments)) * mortgage_rate / 12 / 100
        interest_repayment[interest_repayment < 0] = 0
        principle_repayment = np.array(repayments) - interest_repayment
        principle_repayment[np.cumsum(principle_repayment) > loan_amount] = 0
        while (max(np.cumsum(principle_repayment))-loan_amount)!=0:
            idx=np.where(np.cumsum(principle_repayment)==max(np.cumsum(principle_repayment)))[0][0]
            delta=abs(max(np.cumsum(principle_repayment))-loan_amount)
            principle_repayment[idx+1] = min(delta,monthly_repayment)
            # print(delta,principle_repayment[idx+1],monthly_repayment)
        total_repayment = interest_repayment + principle_repayment
        extra_cost = misc_costs + max(np.cumsum(interest_repayment))
        self.extra_costs_display.set(
            f"Total Extra Cost: ${extra_cost:,.2f} ({extra_cost * 100 / raw_house_cost:.1f}% of house value)")
        self.eff_house_cost_display.set(
            f"Effective house cost: ${extra_cost + raw_house_cost:,.2f}")

        cumulative_rent = months * monthly_rent * ((1 + inflation / 12. / 100.) ** months)
        house_valuation = raw_house_cost * ((1 + house_inflation / 12. / 100.) ** months)
        other_costs = months * nebenkosten * ((1 + inflation / 12. / 100.) ** months)

        owed_to_bank = loan_amount - np.cumsum(principle_repayment)
        total_cumulative_costs = np.cumsum(total_repayment) + upfront_costs
        profit = house_valuation - owed_to_bank - total_cumulative_costs

        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()

        # Update first subplot (House buying costs)
        self.ax1.plot(months, np.cumsum(principle_repayment), lw=2, label='Principle Repayment')
        self.ax1.plot(months, np.cumsum(interest_repayment), lw=2,
                      label="Interest Repayment [" + str(round(max(np.cumsum(interest_repayment)), 0)) + "]")
        self.ax1.plot(months, np.cumsum(principle_repayment) + np.cumsum(interest_repayment) + upfront_costs, lw=2,
                      label="Principle + Interest + Misc. + Downpayment")
        self.ax1.plot(months, cumulative_rent, lw=2, label="Cumulative Rent")
        self.ax1.plot(months, house_valuation, lw=2, label="House Valuation")
        self.ax1.axhline(loan_amount, color="k", linestyle="--", label="Loan Amount")
        self.ax1.axhline(raw_house_cost + misc_costs, color="m", linestyle="-", label="Practical house cost", lw=2)
        self.ax1.axhline(raw_house_cost, color="c", linestyle="-.", label="Raw house cost", lw=1,alpha=0.7)
        self.ax1.axhline(extra_cost, color="gray", linestyle="-", label="Extra house buying cost", lw=2)
        self.ax1.set_title("House buying costs", fontsize=12)
        self.ax1.legend(loc='upper left')
        self.ax1.grid()
        self.ax1.set_ylabel("Amount ($)", fontsize=10)

        # Update second subplot (House valuation vs Rent Analysis)
        delta_min=((-profit) - (cumulative_rent - other_costs))**2
        idx=np.where(delta_min==min(delta_min))[0][0]
        self.ax2.plot(months, -profit, lw=2, label="Negative Profit = (House eval - owed_to_bank - cum. cost)")
        self.ax2.plot(months, cumulative_rent - other_costs, lw=2, label="Cumulative Rent - Other Costs")
        self.ax2.plot(months, cumulative_rent, lw=2, label="Cumulative Rent")
        self.ax2.axhline(0, color="k", linestyle="--")
        self.ax2.set_title("House valuation vs Rent Analysis", fontsize=12)
        self.ax2.legend(loc='upper left')
        self.ax2.grid()
        self.ax2.set_ylim(-profit[idx]-(-profit[idx]*2),-profit[idx]+(-profit[idx]*2))
        self.ax2.set_xlabel("Years", fontsize=10)
        self.ax2.set_ylabel("Money lost ($)", fontsize=10)

        # Set common x-axis ticks (only show years)
        years = np.arange(1, loan_period + 1)
        self.ax2.set_xticks(years * 12)
        self.ax2.set_xticklabels(years)

        # Adjust layout to prevent overlap
        self.figure.tight_layout()

        # Redraw canvas
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = HouseCalculatorApp(root)
    root.mainloop()