let skills = [];
const localStorageKey = 'mySkillsArray';

function loadSkillsFromLocalStorage() {
  const storedSkillsJson = localStorage.getItem(localStorageKey);
  if (storedSkillsJson) {
    try {
      const loadedSkills = JSON.parse(storedSkillsJson);
      if (Array.isArray(loadedSkills)) {
        return loadedSkills;
      } else {
        console.error('Данные в localStorage не являются массивом.');
        return [];
      }
    } catch (e) {
      console.error('Ошибка при парсинге JSON из localStorage:', e);
      return [];
    }
  }
  return [];
}

function saveSkillsToLocalStorage(currentSkillsArray) {
  const jsonString = JSON.stringify(currentSkillsArray);
  localStorage.setItem(localStorageKey, jsonString);
}

skills = loadSkillsFromLocalStorage();

const addSkillBtn = document.querySelector(".add-skill");
const skillList = document.querySelector(".skill-list-block");
const deleteSkill = document.querySelector(".delete-skill")


addSkillBtn.addEventListener("click", e => {
    e.preventDefault();

    const addSkill = prompt("Добавьте новый навык:");

    if (addSkill !== null && addSkill.trim() !== "") {
        const trimmedSkill = addSkill.trim();
        
        skills.push(trimmedSkill);
        
        saveSkillsToLocalStorage(skills);
        
        renderSkillsList(); 
    }
});

function renderSkillsList() {
    skillList.innerHTML = ''; 
    
    skills.forEach((skill, i)=> {
        const deleteElement = document.createElement('button')
        const skillElement = document.createElement('div'); 
        deleteElement.textContent = '⨯'
        deleteElement.classList.add("delete-skill")

        skillElement.textContent = skill;
        skillElement.classList.add("skill-el")
        skillElement.classList.add(`el-${i}`)
        skillElement.appendChild(deleteElement)
        skillList.appendChild(skillElement);

        deleteElement.addEventListener("click", e => {
            e.preventDefault();

            const skillToRemove = skillElement;

            if (skillToRemove && skillToRemove.parentNode) {
                skillToRemove.parentNode.removeChild(skillToRemove);
            }

            skills.splice(i, 1);

            saveSkillsToLocalStorage(skills);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    renderSkillsList(); 
});
