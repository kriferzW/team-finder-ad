// Project-specific JS (complete project action + toggle participate)
(function(){
  document.addEventListener("DOMContentLoaded", function() {
    const completeBtn = document.getElementById("complete-project-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const projectId = completeBtn.dataset.id;
        if (!projectId) return;

        fetch(`/projects/${projectId}/complete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === "ok") {
            const statusEl = document.querySelector(".project-status-black");
            if (statusEl) statusEl.textContent = "Закрыт";
            completeBtn.remove();
            if (window.toast) window.toast("Проект завершён", { type: 'info' });
          } else {
            if (window.toast) window.toast("Ошибка при завершении проекта", { type: 'error' });
            else alert("Ошибка при завершении проекта");
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        });
      });
    }

    document.addEventListener("click", function(e) {
      const btn = e.target.closest("#participate-btn, .card-participate-btn");
      if (!btn) return;
      
      e.preventDefault();
      const projectId = btn.dataset.project;
      if (!projectId) return;

      fetch(`/projects/${projectId}/toggle-participate/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      })
      .then(resp => resp.json())
      .then(data => {
        if (data.status !== "ok") {
          if (window.toast) window.toast("Ошибка при изменении участия", { type: 'error' });
          else alert("Ошибка при изменении участия");
          return;
        }

        const isCardBtn = btn.classList.contains("card-participate-btn");

        if (data.participant) {
          btn.textContent = isCardBtn ? "Ливнуть" : "Отказаться от участия";
          if (isCardBtn) {
            btn.classList.add("participating");
          }

          // Обновляем количество участников на карточке
          const card = btn.closest(".project-card");
          if (card) {
            const countEl = card.querySelector(".participants-count-val");
            if (countEl) {
              const newCount = parseInt(countEl.textContent) + 1;
              countEl.textContent = newCount;
              updateParticipantsWord(card.querySelector(".participants-count-text"), newCount);
            }
          }

          // Обновляем список участников на детальной странице (если есть)
          const participantsList = document.getElementById("participants-list");
          const participantsCount = document.getElementById("participants-count");
          if (participantsList && participantsCount) {
            const userId = btn.dataset.userId || null;
            const userName = btn.dataset.userName || "";
            const userAvatar = btn.dataset.userAvatar || "";
            
            const noParticipants = document.getElementById("no-participants");
            if (noParticipants) noParticipants.remove();

            const a = document.createElement("a");
            a.href = `/users/${userId}`;
            a.id = `participant-${userId}`;
            a.innerHTML = `
              <div class="participant-item">
                <img src="${userAvatar}" alt="Аватар" class="participant-avatar">
                <div class="participant-info">
                  <span class="participant-name">${userName}</span>
                  <span class="participant-role">Участник</span>
                </div>
              </div>
            `;
            participantsList.appendChild(a);
            participantsCount.textContent = parseInt(participantsCount.textContent) + 1;
          }

        } else {
          btn.textContent = isCardBtn ? "Присоединиться" : "Участвовать";
          if (isCardBtn) {
            btn.classList.remove("participating");
          }

          // Обновляем количество участников на карточке
          const card = btn.closest(".project-card");
          if (card) {
            const countEl = card.querySelector(".participants-count-val");
            if (countEl) {
              const newCount = parseInt(countEl.textContent) - 1;
              countEl.textContent = newCount;
              updateParticipantsWord(card.querySelector(".participants-count-text"), newCount);
            }
          }

          // Обновляем список участников на детальной странице (если есть)
          const participantsList = document.getElementById("participants-list");
          const participantsCount = document.getElementById("participants-count");
          if (participantsList && participantsCount) {
            const userId = btn.dataset.userId || null;
            const el = document.getElementById(`participant-${userId}`);
            if (el) el.remove();

            const newCount = parseInt(participantsCount.textContent) - 1;
            participantsCount.textContent = newCount;

            if (newCount === 0) {
              const p = document.createElement("p");
              p.id = "no-participants";
              p.textContent = "Пока нет участников";
              participantsList.appendChild(p);
            }
          }
        }
      })
      .catch(err => {
        console.error("Ошибка запроса:", err);
        if (window.toast) window.toast("Ошибка сети", { type: 'error' });
      });
    });

    function updateParticipantsWord(textEl, count) {
      if (!textEl) return;
      if (count % 100 >= 11 && count % 100 <= 14) {
        textEl.textContent = " участников";
      } else if (count % 10 === 1) {
        textEl.textContent = " участник";
      } else if (count % 10 >= 2 && count % 10 <= 4) {
        textEl.textContent = " участника";
      } else {
        textEl.textContent = " участников";
      }
    }
  });
})();
