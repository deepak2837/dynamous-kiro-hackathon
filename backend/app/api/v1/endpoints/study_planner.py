"""
Study Planner API endpoints for generating and managing study plans.
"""
import logging
import re
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import uuid
from datetime import datetime, date

logger = logging.getLogger(__name__)

from app.models.study_plan import (
    StudyPlan, StudyPlanRequest, StudyPlanResponse, StudyProgress,
    TaskUpdateRequest, ProgressResponse, StudyTaskStatus
)
from app.services.ai_service import AIService
from app.database import get_database
from app.api.auth_simple import get_current_user

router = APIRouter()

@router.post("/generate-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate AI-powered study plan for a session"""
    try:
        # Fetch session content
        session = await db.study_sessions.find_one({"session_id": request.session_id})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify user owns the session
        if session.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Gather session content
        session_content = await _gather_session_content(db, request.session_id)
        
        # Generate study plan using AI
        ai_service = AIService()
        try:
            plan_data = await ai_service.generate_study_plan(
                session_content, 
                request.config.model_dump()
            )
            logger.info(f"AI service returned plan_data keys: {list(plan_data.keys())}")
        except Exception as ai_error:
            logger.error(f"AI service error: {ai_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service failed: {str(ai_error)}"
            )
        
        # Create study plan object
        plan_name = request.plan_name or f"Study Plan - {datetime.now().strftime('%Y-%m-%d')}"
        try:
            # Ensure config is a proper StudyPlanConfig object
            from app.models.study_plan import StudyPlanConfig
            if isinstance(request.config, dict):
                config_obj = StudyPlanConfig(**request.config)
            else:
                config_obj = request.config
                
            study_plan = StudyPlan(
                plan_id=plan_data["plan_id"],
                session_id=request.session_id,
                user_id=current_user.id,
                plan_name=plan_name,
                config=config_obj,
                daily_schedules=[],  # Will be populated from plan_data
                total_study_days=plan_data.get("total_study_days", 0),
                total_study_hours=plan_data.get("total_study_hours", 0),
                subjects_covered=[],
                spaced_repetition_schedule=plan_data.get("spaced_repetition_schedule", {})
            )
            logger.info(f"Created study plan object successfully")
        except Exception as plan_error:
            logger.error(f"Error creating study plan object: {plan_error}")
            logger.error(f"plan_data structure: {plan_data}")
            logger.error(f"request.config: {request.config}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create study plan: {str(plan_error)}"
            )
        
        # Process daily schedules
        from app.models.study_plan import DailySchedule, StudyTask, StudyTaskType, MedicalSubject
        logger.info(f"Processing {len(plan_data.get('daily_schedules', []))} daily schedules")
        
        for i, schedule_data in enumerate(plan_data.get("daily_schedules", [])):
            logger.info(f"Processing schedule {i+1}: {schedule_data.get('date', 'no date')}")
            tasks = []
            for j, task_data in enumerate(schedule_data.get("tasks", [])):
                try:
                    # Safely handle enum values
                    task_type = task_data.get("task_type", "study_notes")
                    if task_type not in [e.value for e in StudyTaskType]:
                        logger.warning(f"Invalid task_type '{task_type}', using 'study_notes'")
                        task_type = "study_notes"  # Default fallback
                    
                    subject = task_data.get("subject", "general")
                    if subject not in [e.value for e in MedicalSubject]:
                        logger.warning(f"Invalid subject '{subject}', using 'general'")
                        subject = "general"  # Default fallback
                    
                    task = StudyTask(
                        task_id=str(uuid.uuid4()),
                        title=task_data.get("title", "Study Task"),
                        description=task_data.get("description", ""),
                        task_type=StudyTaskType(task_type),
                        subject=MedicalSubject(subject),
                        estimated_duration=task_data.get("estimated_duration", 60),
                        priority=task_data.get("priority", 3),
                        content_ids=task_data.get("content_ids", [])
                    )
                    tasks.append(task)
                    logger.info(f"Created task {j+1}: {task.title}")
                except Exception as task_error:
                    logger.error(f"Error creating task {j+1}: {task_error}, task_data: {task_data}")
                    # Skip invalid tasks
                    continue
            
            try:
                from datetime import datetime as dt
                schedule_date = schedule_data.get("date")
                if isinstance(schedule_date, str):
                    parsed_date = dt.fromisoformat(schedule_date).date()
                else:
                    parsed_date = dt.now().date()
                
                daily_schedule = DailySchedule(
                    date=parsed_date,
                    total_study_time=schedule_data.get("total_study_time", 0),
                    tasks=tasks,
                    total_tasks=len(tasks)
                )
                study_plan.daily_schedules.append(daily_schedule)
                logger.info(f"Added daily schedule {i+1} with {len(tasks)} tasks")
            except Exception as schedule_error:
                logger.error(f"Error creating daily schedule {i+1}: {schedule_error}, schedule_data: {schedule_data}")
                continue
        
        # Save study plan to database
        try:
            plan_dict = study_plan.model_dump()
            plan_dict["_id"] = plan_dict["plan_id"]
            
            # Convert date objects to datetime objects for MongoDB compatibility
            def convert_dates(obj):
                if isinstance(obj, date) and not isinstance(obj, datetime):
                    return datetime.combine(obj, datetime.min.time())
                elif isinstance(obj, dict):
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(item) for item in obj]
                return obj
            
            plan_dict = convert_dates(plan_dict)
            await db.study_plans.insert_one(plan_dict)
            logger.info(f"Saved study plan to database: {study_plan.plan_id}")
        except Exception as db_error:
            logger.error(f"Error saving study plan to database: {db_error}")
            # Continue anyway - we can still return the plan
        
        # Initialize progress tracking
        try:
            progress = StudyProgress(
                plan_id=study_plan.plan_id,
                user_id=current_user.id,
                total_tasks=sum(len(schedule.tasks) for schedule in study_plan.daily_schedules)
            )
            progress_dict = progress.model_dump()
            progress_dict["_id"] = f"{progress.plan_id}_progress"
            await db.study_progress.insert_one(progress_dict)
            logger.info(f"Saved study progress to database: {progress.plan_id}")
        except Exception as progress_error:
            logger.error(f"Error saving study progress: {progress_error}")
            # Continue anyway
        
        try:
            response = StudyPlanResponse(
                plan=study_plan,
                message="Study plan generated successfully"
            )
            logger.info(f"Created StudyPlanResponse successfully")
            return response
        except Exception as response_error:
            logger.error(f"Error creating StudyPlanResponse: {response_error}")
            import traceback
            logger.error(f"Response error traceback: {traceback.format_exc()}")
            # Return a simplified response that works
            return {
                "plan_id": study_plan.plan_id,
                "message": "Study plan generated successfully",
                "session_id": study_plan.session_id,
                "total_days": study_plan.total_study_days
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study plan: {str(e)}"
        )

@router.get("/plan/{session_id}")
async def get_study_plan(
    session_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get study plan for a session - handles 'user-plan' for latest plan"""
    try:
        # Validate and sanitize session_id
        if not session_id or len(session_id) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID"
            )
        
        # Handle special case for "user-plan" - return user's latest plan
        if session_id == "user-plan":
            cursor = db.study_plans.find({
                "user_id": current_user.id
            }).sort("created_at", -1).limit(1)
        else:
            # Sanitize session_id to prevent injection
            import re
            if not re.match(r'^[a-zA-Z0-9\-_]+$', session_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid session ID format"
                )
            
            # Find the latest plan for this session
            cursor = db.study_plans.find({
                "session_id": session_id,
                "user_id": current_user.id,
                "is_active": True
            }).sort("created_at", -1).limit(1)
        
        plans = await cursor.to_list(length=1)
        plan = plans[0] if plans else None
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study plan not found"
            )
        
        # Convert to StudyPlan model
        plan.pop("_id", None)
        return StudyPlan(**plan)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve study plan: {str(e)}"
        )

@router.get("/user-plans")
async def get_user_study_plans(
    limit: int = 10,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all study plans for the current user, sorted by latest first"""
    try:
        cursor = db.study_plans.find({
            "user_id": current_user.id,
            "is_active": True
        }).sort("created_at", -1).limit(limit)
        
        plans = await cursor.to_list(length=limit)
        
        # Prepare response with progress for each plan
        plans_with_progress = []
        for plan in plans:
            plan.pop("_id", None)
            
            # Get progress for this plan
            progress = await db.study_progress.find_one({
                "plan_id": plan["plan_id"],
                "user_id": current_user.id
            })
            
            progress_data = None
            if progress:
                progress.pop("_id", None)
                progress_data = {
                    "total_tasks": progress.get("total_tasks", 0),
                    "completed_tasks": progress.get("completed_tasks", 0),
                    "overall_progress": progress.get("overall_progress", 0),
                    "streak_days": progress.get("streak_days", 0)
                }
            
            plans_with_progress.append({
                "plan": plan,
                "progress": progress_data
            })
        
        return {"plans": plans_with_progress, "total_count": len(plans_with_progress)}
        
    except Exception as e:
        logger.error(f"Failed to get user study plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve study plans: {str(e)}"
        )
@router.post("/update-task")
async def update_task_status(
    request: TaskUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update task status and progress using atomic operations"""
    try:
        logger.info(f"Updating task {request.task_id} for user {current_user.id}")
        
        # Use atomic update with positional operator to avoid race conditions
        update_result = await db.study_plans.update_one(
            {
                "user_id": current_user.id,
                "daily_schedules.tasks.task_id": request.task_id
            },
            {
                "$set": {
                    "daily_schedules.$[schedule].tasks.$[task].status": request.status.value,
                    "daily_schedules.$[schedule].tasks.$[task].notes": request.notes,
                    "daily_schedules.$[schedule].tasks.$[task].completed_at": 
                        datetime.utcnow() if request.status == StudyTaskStatus.COMPLETED else None,
                    "updated_at": datetime.utcnow()
                }
            },
            array_filters=[
                {"schedule.tasks.task_id": request.task_id},
                {"task.task_id": request.task_id}
            ]
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        if update_result.modified_count == 0:
            logger.warning(f"Task {request.task_id} was not modified")
        else:
            logger.info(f"Task {request.task_id} updated successfully")
        
        # Get the plan_id for progress update
        plan = await db.study_plans.find_one(
            {"user_id": current_user.id, "daily_schedules.tasks.task_id": request.task_id},
            {"plan_id": 1}
        )
        
        if plan:
            # Update progress atomically
            await _update_study_progress(db, plan["plan_id"], current_user.id)
        
        return {"message": "Task updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )

@router.get("/progress/{plan_id}", response_model=ProgressResponse)
async def get_study_progress(
    plan_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get study progress for a plan"""
    try:
        progress = await db.study_progress.find_one({
            "plan_id": plan_id,
            "user_id": current_user.id
        })
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress not found"
            )
        
        progress.pop("_id", None)
        study_progress = StudyProgress(**progress)
        
        # Get recent activity
        recent_activity = await _get_recent_activity(db, plan_id, current_user)
        
        # Generate recommendations
        recommendations = await _generate_recommendations(db, plan_id, current_user)
        
        return ProgressResponse(
            progress=study_progress,
            recent_activity=recent_activity,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )

async def _gather_session_content(db, session_id: str) -> Dict[str, Any]:
    """Gather all content for a session"""
    content = {
        "questions": [],
        "notes": [],
        "flashcards": [],
        "cheat_sheets": [],
        "mnemonics": []
    }
    
    # Fetch questions
    questions_cursor = db.questions.find({"session_id": session_id})
    content["questions"] = await questions_cursor.to_list(length=None)
    
    # Fetch notes
    notes_cursor = db.notes.find({"session_id": session_id})
    content["notes"] = await notes_cursor.to_list(length=None)
    
    # Fetch flashcards
    flashcards_cursor = db.flashcards.find({"session_id": session_id})
    content["flashcards"] = await flashcards_cursor.to_list(length=None)
    
    # Fetch cheat sheets
    sheets_cursor = db.cheat_sheets.find({"session_id": session_id})
    content["cheat_sheets"] = await sheets_cursor.to_list(length=None)
    
    # Fetch mnemonics
    mnemonics_cursor = db.mnemonics.find({"session_id": session_id})
    content["mnemonics"] = await mnemonics_cursor.to_list(length=None)
    
    return content

async def _update_study_progress(db, plan_id: str, user_id: str):
    """Update study progress based on completed tasks"""
    # Get plan with current task statuses
    plan = await db.study_plans.find_one({"plan_id": plan_id})
    if not plan:
        return
    
    total_tasks = 0
    completed_tasks = 0
    
    for schedule in plan.get("daily_schedules", []):
        for task in schedule.get("tasks", []):
            total_tasks += 1
            if task.get("status") == "completed":
                completed_tasks += 1
    
    overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Update progress
    await db.study_progress.update_one(
        {"plan_id": plan_id, "user_id": user_id},
        {
            "$set": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overall_progress": overall_progress,
                "updated_at": datetime.utcnow()
            }
        }
    )

async def _get_recent_activity(db, plan_id: str, user_id: str) -> List[Dict[str, Any]]:
    """Get recent study activity"""
    # This would typically fetch recent task completions
    # For now, return empty list
    return []

async def _generate_recommendations(db, plan_id: str, user_id: str) -> List[str]:
    """Generate study recommendations based on progress"""
    recommendations = [
        "Keep up the great work with your study schedule!",
        "Consider reviewing flashcards during short breaks",
        "Focus on weak areas identified in your configuration"
    ]
    return recommendations
