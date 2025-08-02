/**
 * Job Card Component for 12thFailJobs.com
 * A reusable component that creates job cards with all essential information
 */

class JobCard {
    /**
     * Create a job card component
     * @param {Object} jobData - The job data object
     * @param {string} jobData.title - Job title
     * @param {string} jobData.company - Company name
     * @param {string} jobData.logo - Company logo URL
     * @param {string} jobData.location - Job location
     * @param {string} jobData.salary - Job salary
     * @param {string} jobData.jobType - Job type (full-time, part-time, etc.)
     * @param {string} jobData.experience - Required experience
     * @param {string} jobData.description - Job description
     * @param {Array<string>} jobData.tags - Job tags/skills
     * @param {string} jobData.badge - Optional badge (Featured, Urgent, Remote, etc.)
     * @param {string} jobData.postedDate - When the job was posted
     * @param {string} jobData.applyLink - Link to apply for the job
     */
    constructor(jobData) {
        this.jobData = jobData;
    }

    /**
     * Render the job card HTML
     * @returns {string} HTML string for the job card
     */
    render() {
        const {
            title,
            company,
            logo,
            location,
            salary,
            jobType,
            experience,
            description,
            tags,
            badge,
            postedDate,
            applyLink
        } = this.jobData;

        // Create tags HTML
        const tagsHTML = tags.map(tag => `<span class="job-tag">${tag}</span>`).join('');

        // Create badge HTML if provided
        const badgeHTML = badge ? `<span class="job-badge">${badge}</span>` : '';

        return `
        <div class="job-card">
            <div class="job-header">
                <div class="company-logo">
                    <img src="${logo}" alt="${company}">
                </div>
                <div class="job-title-company">
                    <h3 class="job-title">${title}</h3>
                    <p class="company-name"><i class="fas fa-building"></i>${company}</p>
                </div>
                ${badgeHTML}
            </div>

            <div class="job-details">
                <div class="job-detail">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${location}</span>
                </div>
                <div class="job-detail">
                    <i class="fas fa-rupee-sign"></i>
                    <span>${salary}</span>
                </div>
                <div class="job-detail">
                    <i class="fas fa-briefcase"></i>
                    <span>${jobType}</span>
                </div>
                <div class="job-detail">
                    <i class="fas fa-user-graduate"></i>
                    <span>${experience}</span>
                </div>
            </div>

            <p class="job-description">${description}</p>

            <div class="job-tags">
                ${tagsHTML}
            </div>

            <div class="job-actions">
                <a href="${applyLink}" class="apply-btn">Apply Now</a>
                <button class="save-job"><i class="far fa-bookmark"></i> Save Job</button>
            </div>

            <p class="posted-date">Posted ${postedDate}</p>
        </div>
        `;
    }

    /**
     * Create a job card and append it to a container
     * @param {HTMLElement} container - The container to append the job card to
     */
    appendTo(container) {
        const jobCardHTML = this.render();
        container.insertAdjacentHTML('beforeend', jobCardHTML);
        
        // Add event listener to the save button
        const jobCards = container.querySelectorAll('.job-card');
        const lastJobCard = jobCards[jobCards.length - 1];
        const saveButton = lastJobCard.querySelector('.save-job');
        
        saveButton.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.backgroundColor = 'rgba(230, 57, 70, 0.1)';
                this.style.color = 'var(--primary-red)';
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.backgroundColor = 'var(--light-gray)';
                this.style.color = 'var(--primary-black)';
            }
        });
    }
}

// Example usage:
// const jobsContainer = document.querySelector('.jobs-container');
//
// const job1 = new JobCard({
//     title: 'Senior Frontend Developer',
//     company: 'Google',
//     logo: 'https://logo.clearbit.com/google.com',
//     location: 'Bangalore, India',
//     salary: '₹18-25 LPA',
//     jobType: 'Full-time',
//     experience: '3-5 Years Experience',
//     description: 'We are looking for an experienced Frontend Developer to join our team. The ideal candidate will have strong skills in React, JavaScript, and modern frontend frameworks.',
//     tags: ['React', 'JavaScript', 'TypeScript', 'CSS3', 'UI/UX'],
//     badge: 'Featured',
//     postedDate: '2 days ago',
//     applyLink: '#'
// });
//
// job1.appendTo(jobsContainer);