import { motion } from 'framer-motion';
import { NavLink, useInRouterContext } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  UserPlus,
  FileText,
  FolderOpen,
  Activity,
  ChevronLeft,
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export const Sidebar = ({ collapsed, setCollapsed }: SidebarProps) => {
  const { t, isRTL } = useLanguage();
  const inRouter = useInRouterContext();
  if (!inRouter) return null;

  const menuItems = [
    { icon: LayoutDashboard, label: t('dashboard'), path: '/' },
    { icon: Users, label: t('patients-list'), path: '/patients' },
    { icon: UserPlus, label: t('add-patient'), path: '/patients/new' },
    { icon: FileText, label: t('medical-history'), path: '/medical-history' },
    { icon: FolderOpen, label: t('documents'), path: '/documents' },
    { icon: Activity, label: t('audit-logs'), path: '/audit-logs' },
  ];

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? '4rem' : '16rem' }}
      className={cn(
        'h-screen bg-sidebar border-r border-sidebar-border flex flex-col',
        'transition-all duration-300 ease-in-out sticky top-0'
      )}
    >
      {/* Logo & Toggle */}
      <div className="p-4 flex items-center justify-between border-b border-sidebar-border">
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-lg text-sidebar-foreground">ClinicOS</span>
          </motion.div>
        )}
        
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="hover:bg-sidebar-accent"
        >
          <ChevronLeft
            className={cn(
              'h-5 w-5 transition-transform',
              collapsed && 'rotate-180',
              isRTL && 'rotate-180'
            )}
          />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {menuItems.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            end
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-all',
                'hover:bg-sidebar-accent hover:shadow-soft',
                isActive
                  ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-medium'
                  : 'text-sidebar-foreground'
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && (
              <span className="text-sm font-medium">
                {item.label}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </motion.aside>
  );
};
