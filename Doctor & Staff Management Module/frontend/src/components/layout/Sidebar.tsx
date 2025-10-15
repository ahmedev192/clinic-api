import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import {
  Users,
  Stethoscope,
  Calendar,
  Shield,
  BookOpen,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Activity,
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar = ({ collapsed, onToggle }: SidebarProps) => {
  const { t } = useLanguage();

  const menuItems = [
    { icon: Activity, label: t('dashboard'), path: '/' },
    { icon: Users, label: t('staff'), path: '/staff' },
    { icon: Stethoscope, label: t('doctors'), path: '/doctors' },
    { icon: Calendar, label: t('schedules'), path: '/schedules' },
    { icon: Shield, label: t('roles'), path: '/roles' },
    { icon: BookOpen, label: t('specializations'), path: '/specializations' },
    { icon: BarChart3, label: t('reports'), path: '/reports' },
  ];

  return (
    <motion.aside
      initial={{ width: 240 }}
      animate={{ width: collapsed ? 80 : 240 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="relative border-r border-sidebar-border bg-sidebar shadow-soft"
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-6">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="flex items-center gap-2"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary shadow-glow">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold text-sidebar-foreground">ClinicOS</span>
            </motion.div>
          )}
          
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-8 w-8 hover:bg-sidebar-accent"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all',
                  'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                  isActive
                    ? 'bg-gradient-primary text-white shadow-glow'
                    : 'text-sidebar-foreground'
                )
              }
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  {item.label}
                </motion.span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="border-t border-sidebar-border p-4"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-primary text-white font-semibold">
                A
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-sidebar-foreground">Admin User</p>
                <p className="text-xs text-sidebar-foreground/60">admin@clinic.com</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.aside>
  );
};
