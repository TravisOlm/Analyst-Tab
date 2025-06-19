// Sidebar.jsx
import { MessageCircle, FileText, DollarSign, TrendingUp, Zap, BriefcaseBusiness, Eye, Menu, Sheet, LogOut, Newspaper, Flame } from "lucide-react";
import { useState, useEffect } from 'react'; 
import { motion, AnimatePresence } from "framer-motion"; 
import { Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";

const SIDEBAR_ITEMS = [
  { name: "Portfolio", icon: DollarSign, color: "#6366f1", href: "/portfolio" },
  { name: "Chatbot", icon: MessageCircle, color: "#6366f1", href: "/chatbot" },
  { name: "All Stocks", icon: TrendingUp, color: "#6366f1", href: "/allstocks" },
  { name: "Upload Portfolio", icon: Sheet, color: "#6366f1", href: "/uploadportfolio" },
  { name: "Vision Model", icon: Eye, color: "#6366f1", href: "/visionmodel" },
  { name: "News", icon : Newspaper, color: "#6366f1", href: "/news" },
  { name: "Simulation", icon: Zap, color: "#6366f1", href: "/momentum" },
  { name: "Analyst", icon: FileText, color: "#6366f1", href: "/analyst" },
  { name: "Portfolio Analyst", icon: BriefcaseBusiness, color: "#6366f1", href: "/portfoliobreakdown" },
  { name: "Heatmap", icon: Flame, color: "#6366f1", href: "/heatmap" },
];

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeChatbot, setActiveChatbot] = useState(1);
  const [infoConversations, setInfoConversations] = useState([]);
  const [personalConversations, setPersonalConversations] = useState([]);

  const handleLogout = () => {
    localStorage.removeItem("userID");
    navigate("/");
  };

  useEffect(() => {
    const userId = localStorage.getItem("userID");
    if (!userId) return;

    axios.get(`http://localhost:8000/get_conversations/?user_id=${userId}`)
      .then(res => setInfoConversations(res.data.conversations || []));

    axios.get(`http://localhost:8000/get_personal_conversations/?user_id=${userId}`)
      .then(res => setPersonalConversations(res.data.conversations || []));
  }, []);

  const startNewConversation = () => {
    const newId = (activeChatbot === 1
      ? (infoConversations[infoConversations.length - 1]?.convo_id || 0)
      : (personalConversations[personalConversations.length - 1]?.convo_id || 0)) + 1;

    navigate(`/chatbot?convo_id=${newId}&chatbot=${activeChatbot}`);
  };

  const renderNavItem = (item) => {
    const isLogout = item.name === "Logout";

    const content = (
      <motion.div
        key={item.href || item.name}
        className='flex items-center p-4 text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors mb-2 cursor-pointer'
        onClick={isLogout ? handleLogout : undefined}
      >
        <item.icon size={20} style={{ color: item.color, minWidth: "20px" }} />
        <AnimatePresence>
          {isSidebarOpen && (
            <motion.span
              className='ml-4 whitespace-nowrap'
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.2, delay: 0.3 }}
            >
              {item.name}
            </motion.span>
          )}
        </AnimatePresence>
      </motion.div>
    );

    return isLogout ? content : <Link to={item.href} key={item.href || item.name}>{content}</Link>;
  };

  return (
    <motion.div className={`relative z-10 transition-all duration-300 ease-in-out flex-shrink-0 ${isSidebarOpen ? 'w-64' : 'w-20'}`} animate={{ width: isSidebarOpen ? 256 : 80 }}>
      <div className='h-full bg-gray-800 bg-opacity-50 backdrop-blur-md p-4 flex flex-col border-r border-gray-700'>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className='p-2 rounded-full hover:bg-gray-700 transition-colors max-w-fit'
        >
          <Menu size={24} />
        </motion.button>

        {/* TOP NAV LINKS */}
        <div className="mt-8">
          {SIDEBAR_ITEMS.map(renderNavItem)}
        </div>

        {/* MID: Chatbot Context */}
        {location.pathname.startsWith("/chatbot") && (
          <div className="flex flex-col mt-4 overflow-y-auto flex-grow pr-1">
            <div className="border-t border-gray-600 my-2" />

            <div className="flex flex-col gap-2 mb-4">
              <button onClick={startNewConversation} className='px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-sm font-semibold'>New Conversation</button>
              <button
                onClick={() => { setActiveChatbot(1); navigate("/chatbot?chatbot=1"); }}
                className={`px-3 py-1 rounded text-sm font-semibold ${activeChatbot === 1 ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
              >Information Bot</button>
              <button
                onClick={() => { setActiveChatbot(2); navigate("/chatbot?chatbot=2"); }}
                className={`px-3 py-1 rounded text-sm font-semibold ${activeChatbot === 2 ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"}`}
              >Personal Bot</button>
            </div>

            {(activeChatbot === 1 ? infoConversations : personalConversations).map((convo) => (
              <Link
                to={`/chatbot?convo_id=${convo.convo_id}&chatbot=${activeChatbot}`}
                key={convo.convo_id}
              >
                <motion.div className='flex items-center py-3 text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors mb-2 cursor-pointer'>
                  {isSidebarOpen && (
                    <span className='ml-3 whitespace-nowrap'>
                      {convo.summary || `Conversation ${convo.convo_id}`}
                    </span>
                  )}
                </motion.div>
              </Link>
            ))}
          </div>
        )}

        {/* LOGOUT */}
        <div className="mt-4">
          {renderNavItem({ name: "Logout", icon: LogOut, color: "#f87171" })}
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;