import { useState, useEffect } from 'react'
import { CheckCircle, Zap, Shield, Star, MessageCircle, CalendarDays, Bot } from 'lucide-react'
import { billingApi } from '@/lib/api'
import { cn } from '@/lib/utils'

const PLANS = [
  {
    id: 'free',
    name: 'Gratis',
    price: '$0',
    period: 'para siempre',
    description: 'Ideal para probar la plataforma',
    icon: Zap,
    color: 'text-slate-600',
    bgColor: 'bg-slate-100',
    features: [
      '50 reservas por mes',
      '1 número de WhatsApp',
      'Bot básico de reservas',
      'Dashboard de reservas',
    ],
    limits: {
      reservations: 50,
    },
  },
  {
    id: 'basic',
    name: 'Básico',
    price: '$19',
    period: 'por mes',
    description: 'Para negocios en crecimiento',
    icon: Shield,
    color: 'text-primary-600',
    bgColor: 'bg-primary-100',
    popular: true,
    features: [
      '500 reservas por mes',
      '1 número de WhatsApp',
      'Bot inteligente con IA',
      'Notificaciones automáticas',
      'Configuración de horarios',
      'Soporte prioritario',
    ],
    limits: {
      reservations: 500,
    },
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$49',
    period: 'por mes',
    description: 'Para negocios establecidos',
    icon: Star,
    color: 'text-warning-600',
    bgColor: 'bg-warning-100',
    features: [
      'Reservas ilimitadas',
      '3 números de WhatsApp',
      'Bot avanzado con IA',
      'Analytics completo',
      'API personalizada',
      'Soporte 24/7',
    ],
    limits: {
      reservations: null,
    },
  },
]

function UsageBar({ used, total, label }) {
  const pct = total ? Math.min((used / total) * 100, 100) : 0
  const color = pct >= 90 ? 'bg-danger-500' : pct >= 70 ? 'bg-warning-500' : 'bg-primary-500'

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-slate-500">{label}</span>
        <span className={cn('font-medium', pct >= 90 ? 'text-danger-600' : 'text-slate-700')}>
          {used} {total ? `/ ${total}` : '/ ∞'}
        </span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', color)}
          style={{ width: total ? `${pct}%` : '0%' }}
          role="progressbar"
          aria-valuenow={used}
          aria-valuemax={total}
          aria-label={label}
        />
      </div>
    </div>
  )
}

export default function BillingPage() {
  const [planInfo, setPlanInfo] = useState(null)
  const [usage, setUsage] = useState(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [pRes, uRes] = await Promise.all([
          billingApi.getPlan(),
          billingApi.getUsage(),
        ])
        setPlanInfo(pRes.data)
        setUsage(uRes.data)
      } catch {
        setPlanInfo({ plan: 'free', status: 'trial' })
        setUsage({ reservations_used: 12, reservations_limit: 50 })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleUpgrade(planId) {
    if (planId === planInfo?.plan) return
    setUpgrading(planId)
    try {
      await billingApi.upgrade(planId)
      setPlanInfo((p) => ({ ...p, plan: planId }))
    } finally {
      setUpgrading('')
    }
  }

  const currentPlan = PLANS.find((p) => p.id === planInfo?.plan) ?? PLANS[0]

  return (
    <div className="flex flex-col gap-7 max-w-4xl animate-fade-in">
      {/* Uso actual */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', currentPlan.bgColor)}>
            <currentPlan.icon size={16} className={currentPlan.color} />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Plan {currentPlan.name}
              {planInfo?.status === 'trial' && (
                <span className="ml-2 badge-yellow text-xs">Período de prueba</span>
              )}
            </p>
            <p className="text-xs text-slate-400">{currentPlan.description}</p>
          </div>
        </div>

        {loading ? (
          <div className="skeleton h-8 rounded-lg" />
        ) : (
          <UsageBar
            label="Reservas este mes"
            used={usage?.reservations_used ?? 0}
            total={usage?.reservations_limit}
          />
        )}
      </div>

      {/* Planes */}
      <div>
        <h2 className="font-display text-lg font-semibold text-slate-900 mb-4">
          Elige tu plan
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PLANS.map((plan, i) => {
            const Icon = plan.icon
            const isCurrent = planInfo?.plan === plan.id
            const isUpgrading = upgrading === plan.id

            return (
              <div
                key={plan.id}
                className={cn(
                  'card p-6 flex flex-col gap-5 relative transition-shadow duration-200',
                  plan.popular ? 'border-primary-300 shadow-card-hover ring-1 ring-primary-200' : '',
                  isCurrent ? 'border-primary-400' : '',
                  `animate-stagger-${i + 1}`,
                )}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="badge-green text-xs px-3 py-1 shadow-sm">Más popular</span>
                  </div>
                )}

                <div>
                  <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center mb-3', plan.bgColor)}>
                    <Icon size={18} className={plan.color} />
                  </div>
                  <p className="font-display text-base font-bold text-slate-900">{plan.name}</p>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-2xl font-display font-bold text-slate-900">{plan.price}</span>
                    <span className="text-sm text-slate-400">{plan.period}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{plan.description}</p>
                </div>

                <ul className="flex flex-col gap-2 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckCircle size={14} className="text-primary-500 flex-shrink-0 mt-0.5" />
                      {f}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isCurrent || isUpgrading}
                  className={cn(
                    'btn w-full justify-center py-2.5 text-sm',
                    isCurrent
                      ? 'bg-slate-100 text-slate-500 cursor-default'
                      : plan.popular
                        ? 'btn-primary'
                        : 'btn-secondary',
                  )}
                >
                  {isUpgrading ? (
                    <span className="w-4 h-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
                  ) : isCurrent ? (
                    'Plan actual'
                  ) : (
                    `Elegir ${plan.name}`
                  )}
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Features highlight */}
      <div className="grid md:grid-cols-3 gap-4 animate-stagger-4">
        {[
          { icon: MessageCircle, title: 'Bot 24/7', desc: 'Tu asistente responde reservas a cualquier hora, sin que tengas que estar presente.' },
          { icon: CalendarDays, title: 'Gestión automática', desc: 'Los horarios se actualizan en tiempo real según las reservas recibidas.' },
          { icon: Bot, title: 'IA conversacional', desc: 'Claude entiende el lenguaje natural de tus clientes y los guía en el proceso.' },
        ].map((f) => (
          <div key={f.title} className="card p-5 flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0">
              <f.icon size={17} className="text-primary-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">{f.title}</p>
              <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{f.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
