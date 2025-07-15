import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Pill, 
  Calendar, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  FileText,
  Download,
  Printer,
  Loader2
} from 'lucide-react';
import { cn } from './lib/utils';

// Types
interface TaperResult {
  warn: string | null;
  patient_instructions: string[];
  ehr_summary: string;
  pharmacy_orders: Array<{ [key: string]: string }>;
  pill_totals: { [key: string]: number };
}

// Form schema
const formSchema = z.object({
  med: z.string().min(1, 'Medication is required'),
  dosing_frequency: z.enum(['once', 'bid', 'tid']),
  am_dose: z.string().min(1, 'AM dose is required').refine((val) => !isNaN(Number(val)) && Number(val) >= 0, {
    message: 'AM dose must be a non-negative number'
  }),
  pm_dose: z.string().min(1, 'PM dose is required').refine((val) => !isNaN(Number(val)) && Number(val) >= 0, {
    message: 'PM dose must be a non-negative number'
  }),
  hs_dose: z.string().optional(),
  speed: z.enum(['slow', 'standard', 'fast', 'very fast', 'ultra fast']),
  start: z.string().min(1, 'Start date is required'),
  final_hold_days: z.string().optional(),
  final_hold_every: z.string().optional(),
  available_strengths: z.array(z.number()).min(1, 'Select at least one tablet strength'),
});

type FormData = z.infer<typeof formSchema>;

const medications = [
  { value: 'alprazolam', label: 'Alprazolam (Xanax)' },
  { value: 'clonazepam', label: 'Clonazepam (Klonopin)' },
  { value: 'lorazepam', label: 'Lorazepam (Ativan)' },
  { value: 'temazepam', label: 'Temazepam (Restoril)' },
  { value: 'oxazepam', label: 'Oxazepam (Serax)' },
  { value: 'chlordiazepoxide', label: 'Chlordiazepoxide (Librium)' },
  { value: 'diazepam', label: 'Diazepam (Valium)' },
];

const speeds = [
  { value: 'slow', label: 'Slow (2.5% every 28 days)' },
  { value: 'standard', label: 'Standard (5% every 21 days)' },
  { value: 'fast', label: 'Fast (10% every 14 days)' },
  { value: 'very fast', label: 'Very Fast (15% every 14 days)' },
  { value: 'ultra fast', label: 'Ultra Fast (20% every 7 days)' },
];

const availableDiazepamStrengths = [
  { value: 10.0, label: '10 mg' },
  { value: 5.0, label: '5 mg' },
  { value: 2.0, label: '2 mg' },
];

function App() {
  const [result, setResult] = useState<TaperResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      med: 'alprazolam',
      dosing_frequency: 'bid',
      am_dose: '',
      pm_dose: '',
      hs_dose: '',
      speed: 'standard',
      start: new Date().toISOString().split('T')[0],
      available_strengths: [10.0, 5.0, 2.0],
    },
  });

  const finalHoldDays = watch('final_hold_days');
  const finalHoldEvery = watch('final_hold_every');

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Calculate total daily dose
      const amDose = parseFloat(data.am_dose) || 0;
      const pmDose = parseFloat(data.pm_dose) || 0;
      const hsDose = parseFloat(data.hs_dose || '0') || 0;
      const totalDose = amDose + pmDose + hsDose;

      const payload = {
        med: data.med,
        dose: totalDose,
        dosing_schedule: {
          frequency: data.dosing_frequency,
          am: amDose,
          pm: pmDose,
          hs: hsDose,
        },
        speed: data.speed,
        start: data.start,
        available_strengths: data.available_strengths,
        final_hold: finalHoldDays && finalHoldEvery 
          ? [parseInt(finalHoldDays), parseInt(finalHoldEvery)]
          : undefined,
      };

      const response = await fetch('/taper', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate taper schedule');
      }

      const resultData = await response.json();
      setResult(resultData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const printSchedule = () => {
    if (!result) return;
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Benzodiazepine Taper Schedule</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .section { margin-bottom: 20px; }
              .warning { color: #dc2626; font-weight: bold; }
              .instructions { white-space: pre-line; }
            </style>
          </head>
          <body>
            <h1>Benzodiazepine Taper Schedule</h1>
            ${result.warn ? `<div class="warning">⚠️ ${result.warn}</div>` : ''}
            <div class="section">
              <h2>Patient Instructions</h2>
              <div class="instructions">${result.patient_instructions.join('\n\n')}</div>
            </div>
            <div class="section">
              <h2>EHR Summary</h2>
              <div class="instructions">${result.ehr_summary}</div>
            </div>
            <div class="section">
              <h2>Pharmacy Orders</h2>
              <div class="instructions">${result.pharmacy_orders.map(order => 
                Object.entries(order).map(([key, value]) => `${key}: ${value}`).join('\n')
              ).join('\n\n')}</div>
            </div>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <Pill className="w-8 h-8 text-primary-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">BZD Taper Generator</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Generate safe, ASAM-compliant benzodiazepine taper schedules with detailed patient instructions, 
            pharmacy orders, and EHR summaries.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
          {/* Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Calendar className="w-6 h-6 mr-2 text-primary-600" />
              Taper Configuration
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Medication */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Medication
                </label>
                <select
                  {...register('med')}
                  className="input-field"
                >
                  {medications.map((med) => (
                    <option key={med.value} value={med.value}>
                      {med.label}
                    </option>
                  ))}
                </select>
                {errors.med && (
                  <p className="mt-1 text-sm text-red-600">{errors.med.message}</p>
                )}
              </div>

              {/* Dosing Frequency */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dosing Frequency
                </label>
                <select
                  {...register('dosing_frequency')}
                  className="input-field"
                >
                  <option value="once">Once daily</option>
                  <option value="bid">Twice daily (BID)</option>
                  <option value="tid">Three times daily (TID)</option>
                </select>
                {errors.dosing_frequency && (
                  <p className="mt-1 text-sm text-red-600">{errors.dosing_frequency.message}</p>
                )}
              </div>

              {/* AM Dose */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Morning Dose (mg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('am_dose')}
                  className="input-field"
                  placeholder="e.g., 1.0"
                />
                {errors.am_dose && (
                  <p className="mt-1 text-sm text-red-600">{errors.am_dose.message}</p>
                )}
              </div>

              {/* PM Dose */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Afternoon/Evening Dose (mg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('pm_dose')}
                  className="input-field"
                  placeholder="e.g., 2.0"
                />
                {errors.pm_dose && (
                  <p className="mt-1 text-sm text-red-600">{errors.pm_dose.message}</p>
                )}
              </div>

              {/* HS Dose (only for TID) */}
              <div className="hidden">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bedtime Dose (mg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('hs_dose')}
                  className="input-field"
                  placeholder="e.g., 1.0"
                />
                {errors.hs_dose && (
                  <p className="mt-1 text-sm text-red-600">{errors.hs_dose.message}</p>
                )}
              </div>

              {/* Available Tablet Strengths */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Diazepam Tablet Strengths
                </label>
                <div className="space-y-2">
                  {availableDiazepamStrengths.map((strength) => (
                    <label key={strength.value} className="flex items-center">
                      <input
                        type="checkbox"
                        value={strength.value}
                        {...register('available_strengths')}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{strength.label}</span>
                    </label>
                  ))}
                </div>
                {errors.available_strengths && (
                  <p className="mt-1 text-sm text-red-600">{errors.available_strengths.message}</p>
                )}
              </div>

              {/* Speed */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Taper Speed
                </label>
                <select
                  {...register('speed')}
                  className="input-field"
                >
                  {speeds.map((speed) => (
                    <option key={speed.value} value={speed.value}>
                      {speed.label}
                    </option>
                  ))}
                </select>
                {errors.speed && (
                  <p className="mt-1 text-sm text-red-600">{errors.speed.message}</p>
                )}
              </div>

              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  {...register('start')}
                  className="input-field"
                />
                {errors.start && (
                  <p className="mt-1 text-sm text-red-600">{errors.start.message}</p>
                )}
              </div>

              {/* Final Hold (Optional) */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Final Hold (Optional)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hold Days
                    </label>
                    <input
                      type="number"
                      {...register('final_hold_days')}
                      className="input-field"
                      placeholder="e.g., 6"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Every N Days
                    </label>
                    <input
                      type="number"
                      {...register('final_hold_every')}
                      className="input-field"
                      placeholder="e.g., 3"
                    />
                  </div>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Leave empty to skip final hold period
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={cn(
                  "w-full btn-primary flex items-center justify-center",
                  loading && "opacity-50 cursor-not-allowed"
                )}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Schedule...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Generate Taper Schedule
                  </>
                )}
              </button>
            </form>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Results */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            {result && (
              <>
                {/* Warning */}
                {result.warn && (
                  <div className="card border-l-4 border-yellow-400 bg-yellow-50">
                    <div className="flex items-start">
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
                      <div>
                        <h3 className="font-medium text-yellow-800">Warning</h3>
                        <p className="text-yellow-700 mt-1">{result.warn}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Patient Instructions */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-primary-600" />
                      Patient Instructions
                    </h3>
                    <button
                      onClick={printSchedule}
                      className="btn-secondary flex items-center text-sm"
                    >
                      <Printer className="w-4 h-4 mr-1" />
                      Print
                    </button>
                  </div>
                  <div className="space-y-3">
                    {result.patient_instructions.map((instruction, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-gray-700 whitespace-pre-line">{instruction}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* EHR Summary */}
                <div className="card">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-primary-600" />
                    EHR Summary
                  </h3>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 whitespace-pre-line">{result.ehr_summary}</p>
                  </div>
                </div>

                {/* Pharmacy Orders */}
                <div className="card">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <Pill className="w-5 h-5 mr-2 text-primary-600" />
                    Pharmacy Orders
                  </h3>
                  <div className="space-y-3">
                    {result.pharmacy_orders.map((order, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        {Object.entries(order).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="font-medium text-gray-700">{key}:</span>
                            <span className="text-gray-600">{value}</span>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pill Totals */}
                <div className="card">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    <Pill className="w-5 h-5 mr-2 text-primary-600" />
                    Pill Totals
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(result.pill_totals).map(([strength, count]) => (
                      <div key={strength} className="flex justify-between p-2 bg-gray-50 rounded">
                        <span className="font-medium text-gray-700">{strength}mg:</span>
                        <span className="text-gray-600">{count} tablets</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {!result && !loading && (
              <div className="card text-center text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>Fill out the form and generate a taper schedule to see results here.</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default App; 