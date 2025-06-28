# Memory Bank - AI Agent Knowledge Base

This directory contains comprehensive documentation and lessons learned for AI agents working on the Hovel project. Use these resources to understand the project architecture, troubleshoot issues, and follow best practices.

## 📚 Available Resources

### 🛠️ Technical Guides
- **[Python Environment Troubleshooting](python-environment-troubleshooting.md)** - Complete guide to resolving Python environment and Flask installation issues in containerized environments
- **[Flask Server Startup Guide](flask-server-startup-guide.md)** - Step-by-step instructions for starting Flask servers with troubleshooting flows

### 📋 Project Planning
- **[Comprehensive Project Plan](project-plan-comprehensive.md)** - Complete project roadmap covering architecture, API specs, Docker setup, development workflow, and future enhancements

## 🎯 Quick Reference for AI Agents

### When Starting the Server
1. Check [Flask Server Startup Guide](flask-server-startup-guide.md) for the correct startup sequence
2. If you encounter ModuleNotFoundError, refer to [Python Environment Troubleshooting](python-environment-troubleshooting.md)
3. Use `/usr/local/bin/python3.11 server.py` as the recommended startup command

### When Troubleshooting Issues
1. **ModuleNotFoundError**: Check Python installations and use specific binary paths
2. **SSL Issues**: Install system SSL packages (libssl-dev, python3-openssl, ca-certificates)
3. **External Environment Management**: Use virtual environments or specific Python binaries
4. **Port Conflicts**: Verify unique port assignment in branch .env files

### When Planning Development
1. Review [Comprehensive Project Plan](project-plan-comprehensive.md) for architecture and API specifications
2. Follow the documented directory structure and development workflow
3. Reference the future enhancements roadmap for feature planning

### When Managing Branches (NEW)
1. **Create branches** using the API: `POST /api/branch`
2. **Verify unique ports** are assigned to each branch
3. **Check .env files** for correct PORT assignments
4. **Test branch isolation** by running multiple branches simultaneously

## 🔍 Search Keywords

Use these keywords to quickly find relevant information:

- **Python environment**: Environment setup, SSL issues, virtual environments
- **Flask server**: Startup commands, troubleshooting, configuration
- **Docker**: Container setup, SSL dependencies, environment isolation
- **API endpoints**: REST API, branch management, health checks
- **Development workflow**: Cursor.dev integration, testing, deployment
- **Architecture**: System design, directory structure, technology stack
- **Port conflicts**: Branch management, unique port assignment, environment isolation

## 📖 How to Use This Knowledge Base

### For New AI Agents
1. Start with the [Comprehensive Project Plan](project-plan-comprehensive.md) to understand the project scope
2. Review the [Flask Server Startup Guide](flask-server-startup-guide.md) for operational procedures
3. Keep the [Python Environment Troubleshooting](python-environment-troubleshooting.md) guide handy for common issues

### For Ongoing Development
1. Reference the project plan for API specifications and architecture decisions
2. Use the troubleshooting guides when encountering environment issues
3. Update the knowledge base with new lessons learned

### For Problem Solving
1. Identify the issue category (environment, server, API, etc.)
2. Search the relevant guide for similar problems
3. Follow the documented troubleshooting sequence
4. Document any new solutions discovered

### For Branch Management (NEW)
1. **Port Conflict Resolution**: ✅ **COMPLETED** - Unique ports are automatically assigned
2. **Environment Isolation**: Each branch runs on its own port (8001, 8002, 8003, etc.)
3. **Verification**: Check .env files and Docker Compose configurations
4. **Testing**: Create multiple branches to verify isolation

## 🎉 Recent Achievements

### Port Conflict Resolution - COMPLETED ✅
**Problem Solved:** Multiple branches were being created with the same port (8000), causing conflicts.

**Solution:** Updated branch creation functions to use unique ports:
- ✅ Each branch gets unique port in .env file
- ✅ Docker Compose uses unique external ports
- ✅ Automatic port increment (8001, 8002, 8003, etc.)
- ✅ No conflicts between running branches

**Impact:**
- 🚀 Multiple branches can run simultaneously
- 🔧 Full environment isolation achieved
- 📊 Scalable branch management for teams

## 🔄 Maintenance

This knowledge base should be updated whenever:
- New issues are encountered and resolved
- Architecture changes are made
- New features are implemented
- Best practices are discovered
- Major problems are solved (like port conflicts)

## 📞 Related Resources

- **Main README**: [../README.md](../README.md) - Project overview and quick start
- **Branch Documentation**: [../docs/BRANCH_README.md](../docs/BRANCH_README.md) - Branch management system
- **API Server**: [../server.py](../server.py) - Main Flask application with port conflict resolution
- **Docker Configuration**: [../Dockerfile](../Dockerfile) - Container setup

---

*This memory bank serves as a comprehensive knowledge base for AI agents working on the Hovel project, ensuring consistent problem-solving approaches and best practices. The recent port conflict resolution demonstrates the value of this knowledge base in solving complex development challenges.* 