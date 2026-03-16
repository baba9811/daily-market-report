import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { CheckCircle, XCircle, Send, RefreshCw } from 'lucide-react'

export default function Settings() {
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: api.settings,
  })
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.healthCheck,
  })

  const [form, setForm] = useState<Record<string, string>>({})

  const updateMutation = useMutation({
    mutationFn: api.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      alert('설정이 저장되었습니다. 서버를 재시작하면 적용됩니다.')
    },
  })

  const testEmailMutation = useMutation({
    mutationFn: api.testEmail,
    onSuccess: (data: any) => {
      alert(data.success ? '테스트 이메일이 전송되었습니다!' : '이메일 전송에 실패했습니다.')
    },
  })

  if (isLoading) return <div className="text-slate-400">로딩 중...</div>

  const s = settings as any
  const h = health as any

  const handleSave = () => {
    const updateData: Record<string, string | number | string[]> = {}
    for (const [key, value] of Object.entries(form)) {
      if (value !== '') {
        if (key === 'smtp_port') {
          updateData[key] = parseInt(value)
        } else if (key === 'email_to') {
          updateData[key] = value.split(',').map((e: string) => e.trim())
        } else {
          updateData[key] = value
        }
      }
    }
    if (Object.keys(updateData).length > 0) {
      updateMutation.mutate(updateData)
    }
  }

  const StatusIcon = ({ ok }: { ok: boolean }) =>
    ok ? <CheckCircle size={16} className="text-accent-green" /> : <XCircle size={16} className="text-accent-red" />

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white">설정</h2>
        <p className="text-sm text-slate-400 mt-1">이메일, API, 스케줄러 설정 관리</p>
      </div>

      {/* Health Status */}
      {h && (
        <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-4">시스템 상태</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <StatusIcon ok={h.database} />
              <span className="text-sm text-slate-300">데이터베이스</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusIcon ok={h.claude_cli} />
              <span className="text-sm text-slate-300">Claude CLI</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusIcon ok={h.smtp_configured} />
              <span className="text-sm text-slate-300">SMTP 설정</span>
            </div>
          </div>
        </div>
      )}

      {/* Email Settings */}
      <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-4">이메일 설정</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1">SMTP Host</label>
            <input
              type="text"
              defaultValue={s?.smtp_host}
              onChange={(e) => setForm({ ...form, smtp_host: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">SMTP Port</label>
            <input
              type="number"
              defaultValue={s?.smtp_port}
              onChange={(e) => setForm({ ...form, smtp_port: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">SMTP User</label>
            <input
              type="email"
              defaultValue={s?.smtp_user}
              onChange={(e) => setForm({ ...form, smtp_user: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">SMTP Password</label>
            <input
              type="password"
              placeholder={s?.smtp_password_set ? '••••••••' : '미설정'}
              onChange={(e) => setForm({ ...form, smtp_password: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">발신자</label>
            <input
              type="email"
              defaultValue={s?.email_from}
              onChange={(e) => setForm({ ...form, email_from: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">수신자 (쉼표 구분)</label>
            <input
              type="text"
              defaultValue={s?.email_to?.join(', ')}
              onChange={(e) => setForm({ ...form, email_to: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleSave}
            className="bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            <RefreshCw size={14} /> 저장
          </button>
          <button
            onClick={() => testEmailMutation.mutate()}
            disabled={testEmailMutation.isPending}
            className="bg-bg-hover hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            <Send size={14} /> 테스트 이메일
          </button>
        </div>
      </div>

      {/* Claude Settings */}
      <div className="bg-bg-card rounded-xl p-6 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-300 mb-4">Claude 설정</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1">CLI Path</label>
            <input
              type="text"
              defaultValue={s?.claude_cli_path}
              onChange={(e) => setForm({ ...form, claude_cli_path: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Model</label>
            <select
              defaultValue={s?.claude_model}
              onChange={(e) => setForm({ ...form, claude_model: e.target.value })}
              className="w-full bg-bg-primary border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:border-accent-blue focus:outline-none"
            >
              <option value="opus">Opus</option>
              <option value="sonnet">Sonnet</option>
              <option value="haiku">Haiku</option>
            </select>
          </div>
        </div>
        <button
          onClick={handleSave}
          className="bg-accent-blue hover:bg-accent-blue/80 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors mt-4 flex items-center gap-2"
        >
          <RefreshCw size={14} /> 저장
        </button>
      </div>
    </div>
  )
}
